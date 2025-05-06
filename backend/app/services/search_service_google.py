#backend/app/services/search_service_google.py

from typing import List, Dict, Any
import uuid
import aiohttp
import json
import time
from sqlalchemy.orm import Session
from app.config import settings
from app.services.disease_service import DiseaseService
from app.services.scraper_service import ScraperService
from app.services.llm_service import LLMService
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate
import logging
import re

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSearchService:
    def __init__(self):
        self.disease_service = DiseaseService()
        self.scraper_service = ScraperService()
        self.llm_service = LLMService()
        self.api_key = settings.GOOGLE_API_KEY
        self.cse_id = settings.GOOGLE_CSE_ID
        self.max_results = settings.GOOGLE_API_MAX_RESULTS
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        # APIキーとCSE IDの検証
        if not self.api_key or not self.cse_id:
            logger.warning("Google API Key または Custom Search Engine ID が設定されていません")
    
    async def generate_search_terms(self, disease_name: str, disease_name_en: str = None, 
                                   custom_keywords: List[str] = None) -> List[str]:
        """検索語を生成"""
        search_terms = []
        
        # 基本的な検索語パターン
        base_terms = []
        if disease_name:
            base_terms.append(disease_name)
        if disease_name_en:
            base_terms.append(disease_name_en)
        
        # カスタムキーワードも追加
        if custom_keywords:
            base_terms.extend(custom_keywords)
        
        # 日本語用の組み合わせ
        ja_suffixes = ['患者会', '患者の会', '家族会', '支援団体', '支援グループ', '協会']
        
        for term in base_terms:
            # 日本語の場合
            if self._is_japanese(term):
                for suffix in ja_suffixes:
                    search_terms.append(f"{term} {suffix}")
            # 英語の場合
            else:
                en_suffixes = ['patient association', 'support group', 'foundation', 'society']
                for suffix in en_suffixes:
                    search_terms.append(f"{term} {suffix}")
        
        # 重複を除去
        return list(set(search_terms))
    
    def _is_japanese(self, text: str) -> bool:
        """日本語かどうかを判定"""
        import re
        return bool(re.search(r'[ぁ-んァ-ン一-龥]', text))
    
    async def search_via_api(self, query: str, start_index: int = 1) -> List[Dict[str, Any]]:
        """Google Custom Search APIを使用して検索"""
        if not self.api_key or not self.cse_id:
            logger.error("Google API KeyとCustom Search Engine IDを設定してください")
            return []
        
        logger.info(f"Google APIで検索: {query} (開始インデックス: {start_index})")
        
        params = {
            'key': self.api_key,
            'cx': self.cse_id,
            'q': query,
            'start': start_index,
            'num': 10,  # 一度に取得する最大数
            'hl': 'ja',  # 日本語結果を優先
            'lr': 'lang_ja',  # 日本語のページを検索
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 結果の処理
                        items = data.get('items', [])
                        results = []
                        
                        for item in items:
                            # PDFファイルなどを除外
                            url = item.get('link', '')
                            if url.endswith('.pdf'):
                                continue
                                
                            results.append({
                                'title': item.get('title', ''),
                                'url': url,
                                'snippet': item.get('snippet', '')
                            })
                        
                        logger.info(f"{len(results)}件の検索結果を取得しました")
                        return results
                    else:
                        error_text = await response.text()
                        logger.error(f"API呼び出しエラー: {response.status}, {error_text}")
                        return []
        except Exception as e:
            logger.error(f"検索中に例外が発生: {str(e)}")
            return []
    
    def is_duplicate_organization(self, new_org: Dict[str, Any], existing_orgs: List[Dict[str, Any]]) -> bool:
        """組織が重複しているかチェック"""
        if not new_org.get("name"):
            return True
            
        # テンプレート値のチェック
        if new_org.get("name") == "団体名" or new_org.get("url") == "ウェブサイトURL":
            return True
            
        # 既存の組織と比較
        for org in existing_orgs:
            # 名前の正規化（空白や記号を除去して比較）
            new_name = re.sub(r'\s+|[　\-\(\)（）]', '', new_org.get("name", "")).lower()
            existing_name = re.sub(r'\s+|[　\-\(\)（）]', '', org.get("name", "")).lower()
            
            # 名前が類似している場合は重複と判定
            if new_name and existing_name and (new_name in existing_name or existing_name in new_name):
                logger.info(f"重複する組織: '{new_org.get('name')}' と '{org.get('name')}'")
                return True
                
            # 連絡先が同じ場合も重複と判定
            if new_org.get("contact") and org.get("contact") and new_org.get("contact") == org.get("contact"):
                logger.info(f"連絡先が同じ組織: {new_org.get('contact')}")
                return True
                
        return False
    
    def extract_url_from_page(self, page_content: Dict[str, Any], org_name: str) -> str:
        """ページ内容からURLを抽出"""
        # ページのURLをデフォルトとして設定
        default_url = page_content.get('url', '')
        
        # ページ内容からURLを検索
        text = page_content.get('text', '')
        
        # URLのパターン
        patterns = [
            r'(https?://[\w\.-]+\.[\w\.-]+(?:/[\w\.-]*)*)/?',  # 一般的なURL
            r'(https?://www\.[\w\.-]+\.[a-zA-Z]{2,})/?',  # www.から始まるURL
            r'(www\.[\w\.-]+\.[a-zA-Z]{2,})/?'  # wwwから始まるURL（http(s)なし）
        ]
        
        # 組織名の近くにあるURLを優先
        org_index = text.find(org_name)
        if org_index != -1:
            # 組織名の前後500文字を検索範囲とする
            search_start = max(0, org_index - 500)
            search_end = min(len(text), org_index + 500)
            search_text = text[search_start:search_end]
            
            for pattern in patterns:
                urls = re.findall(pattern, search_text)
                if urls:
                    for url in urls:
                        # URLが有効かチェック
                        if not url.startswith('http'):
                            url = 'https://' + url
                        return url
        
        # ページ全体からURLを検索（上記で見つからない場合）
        for pattern in patterns:
            urls = re.findall(pattern, text)
            if urls:
                for url in urls:
                    # URLが有効かチェック
                    if not url.startswith('http'):
                        url = 'https://' + url
                    return url
        
        return default_url
    
    async def search_organizations(self, db: Session, disease_id: str, 
                                  max_terms: int = 3, 
                                  max_results_per_term: int = 5) -> List[Dict[str, Any]]:
        """疾患に関連する組織を検索"""
        logger.info(f"disease_id: {disease_id} の検索を開始")
        
        disease = self.disease_service.get_disease(db, disease_id)
        if not disease:
            logger.error(f"疾患が見つかりません: {disease_id}")
            return []
        
        logger.info(f"疾患を検索: {disease.name}")
        
        # 検索語を生成
        search_terms = await self.generate_search_terms(disease.name, disease.name_en)
        logger.info(f"生成された検索語: {search_terms}")
        
        all_organizations = []
        
        # 検索語ごとに処理（上限あり）
        for term in search_terms[:max_terms]:
            logger.info(f"検索語で検索中: {term}")
            
            # Google APIを使用して検索
            search_results = await self.search_via_api(term)
            logger.info(f"{len(search_results)}件の検索結果を取得")
            
            if not search_results:
                logger.info(f"検索語の結果なし: {term}")
                continue
            
            # 各検索結果を処理（上限あり）
            for i, result in enumerate(search_results[:max_results_per_term]):
                logger.info(f"結果を処理中 {i+1}: {result['url']}")
                
                try:
                    # ページの内容を取得
                    page_content = await self.scraper_service.fetch_page_content(result['url'])
                    
                    if not page_content['success']:
                        logger.error(f"{result['url']}からのコンテンツ取得に失敗: {page_content.get('error')}")
                        continue
                    
                    logger.info(f"{result['url']}からコンテンツを取得しました")
                    
                    # LLMで組織情報を抽出
                    org_info = await self.llm_service.extract_organization_info(
                        page_content['text'], 
                        disease.name
                    )
                    
                    logger.info(f"LLMで情報を抽出: {org_info}")
                    
                    # 抽出された組織情報を保存
                    for org in org_info.get('organizations', []):
                        # 重複チェック
                        if self.is_duplicate_organization(org, all_organizations):
                            continue
                        
                        # URLがない場合、ページ内容から可能な限り抽出
                        if not org.get('url') or org.get('url') == "" or org.get('url') == "不明":
                            org['url'] = self.extract_url_from_page(page_content, org.get('name', ''))
                        
                        # 組織情報のオブジェクトを作成
                        org_data = OrganizationCreate(
                            disease_id=disease_id,
                            name=org.get('name', ''),
                            url=org.get('url', result['url']),
                            description=org.get('description', ''),
                            contact=org.get('contact', ''),
                            type=org.get('type', 'support'),
                            source_url=result['url'],
                            relevance_score=90.0  # デフォルトスコア
                        )
                        
                        # DBに保存
                        org_id = str(uuid.uuid4())
                        db_org = Organization(
                            id=org_id,
                            **org_data.dict()
                        )
                        db.add(db_org)
                        
                        all_organizations.append({
                            'id': org_id,
                            **org_data.dict(),
                            'verification_status': 'pending'
                        })
                        
                        logger.info(f"組織を追加: {org.get('name')}")
                    
                except Exception as e:
                    logger.error(f"結果の処理中にエラー: {e}")
                    continue
                
                # API制限を避けるための遅延
                time.sleep(1)
        
        db.commit()
        logger.info(f"合計{len(all_organizations)}件の組織を発見")
        return all_organizations
