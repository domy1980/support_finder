#backend/app/services/search_services_google.py

from typing import List, Dict, Any
import uuid
from sqlalchemy.orm import Session
from app.services.disease_service import DiseaseService
from app.services.scraper_service import ScraperService
from app.services.llm_service import LLMService
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate
import time

class SearchService:
    def __init__(self):
        self.disease_service = DiseaseService()
        self.scraper_service = ScraperService()
        self.llm_service = LLMService()
    
    async def generate_search_terms(self, disease_name: str, disease_name_en: str = None) -> List[str]:
        """検索語を生成"""
        search_terms = []
        
        # 基本的な検索語パターン
        base_terms = []
        if disease_name:
            base_terms.append(disease_name)
        if disease_name_en:
            base_terms.append(disease_name_en)
        
        # 日本語用の組み合わせ
        ja_suffixes = ['患者会', '家族会', '支援団体', '支援グループ', '患者の会', '協会']
        
        for term in base_terms:
            # 日本語の場合
            if self._is_japanese(term):
                for suffix in ja_suffixes:
                    search_terms.append(f"{term} {suffix}")
                    search_terms.append(f"{term}　{suffix}")  # 全角スペース
            # 英語の場合
            else:
                en_suffixes = ['patient association', 'support group', 'foundation', 'society', 'patients']
                for suffix in en_suffixes:
                    search_terms.append(f"{term} {suffix}")
        
        # 重複を除去
        return list(set(search_terms))
    
    def _is_japanese(self, text: str) -> bool:
        """日本語かどうかを判定"""
        import re
        return bool(re.search(r'[ぁ-んァ-ン一-龥]', text))
    
    async def search_organizations(self, db: Session, disease_id: str) -> List[Dict[str, Any]]:
        """疾患に関連する組織を検索"""
        print(f"Starting search for disease_id: {disease_id}")
        
        disease = self.disease_service.get_disease(db, disease_id)
        if not disease:
            print(f"Disease not found: {disease_id}")
            return []
        
        print(f"Searching for disease: {disease.name}")
        
        # 検索語を生成
        search_terms = await self.generate_search_terms(disease.name, disease.name_en)
        print(f"Generated search terms: {search_terms}")
        
        all_organizations = []
        
        for term in search_terms[:3]:  # 最初の3つの検索語のみ使用（API制限回避）
            print(f"Searching with term: {term}")
            
            # Web検索
            search_results = await self.scraper_service.search_web(term)
            print(f"Found {len(search_results)} search results")
            
            if not search_results:
                print(f"No search results for term: {term}")
                continue
            
            for i, result in enumerate(search_results[:5]):  # 各検索語で上位5件のみ処理
                print(f"Processing result {i+1}: {result['url']}")
                
                try:
                    # ページの内容を取得
                    page_content = await self.scraper_service.fetch_page_content(result['url'])
                    
                    if not page_content['success']:
                        print(f"Failed to fetch content from {result['url']}: {page_content.get('error')}")
                        continue
                    
                    print(f"Successfully fetched content from {result['url']}")
                    
                    # LLMで組織情報を抽出
                    org_info = await self.llm_service.extract_organization_info(
                        page_content['text'], 
                        disease.name
                    )
                    
                    print(f"LLM extracted info: {org_info}")
                    
                    # 抽出された組織情報を保存
                    for org in org_info.get('organizations', []):
                        # 関連性を検証
                        verification = await self.llm_service.verify_relevance(org, disease.name)
                        print(f"Verification result: {verification}")
                        
                        if verification.get('is_relevant', False):
                            org_data = OrganizationCreate(
                                disease_id=disease_id,
                                name=org.get('name', ''),
                                url=org.get('url', result['url']),
                                description=org.get('description', ''),
                                contact=org.get('contact', ''),
                                type=org.get('type', 'support'),
                                source_url=result['url'],
                                relevance_score=verification.get('relevance_score', 0)
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
                            
                            print(f"Added organization: {org.get('name')}")
                    
                except Exception as e:
                    print(f"Error processing result: {e}")
                    continue
                
                # API制限を避けるための遅延
                time.sleep(1)
        
        db.commit()
        print(f"Found {len(all_organizations)} organizations total")
        return all_organizations
