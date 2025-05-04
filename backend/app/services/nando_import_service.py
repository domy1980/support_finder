import pandas as pd
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.disease import Disease, DiseaseSynonym, DiseaseCustomKeyword
import uuid

class NandoImportService:
    def __init__(self):
        pass
    
    def import_nando_data(self, db: Session, file_path: str) -> Dict[str, Any]:
        """NANDOデータをインポート"""
        try:
            df = pd.read_excel(file_path, sheet_name='Sheet1')
            
            imported_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    nando_id = str(row['NANDO ID'])
                    disease_type = self._determine_disease_type(nando_id)
                    name_ja = row['疾患名（日本語）']
                    name_en = row['疾患名（英語）'] if pd.notna(row['疾患名（英語）']) else None
                    
                    # 既存の疾患をチェック
                    existing = db.query(Disease).filter(Disease.nando_id == nando_id).first()
                    
                    disease_data = {
                        'nando_id': nando_id,
                        'name': name_ja,
                        'name_en': name_en,
                        'disease_type': disease_type,
                        'is_designated_intractable': disease_type == 'designated' and pd.notna(row['告示番号']),
                        'is_chronic_childhood': disease_type == 'chronic_childhood' and pd.notna(row['小児慢性特定疾病情報センター']),
                        'parent_disease_id': row['親NANDO ID'] if pd.notna(row['親NANDO ID']) else None,
                    }
                    
                    # 告示番号があれば追加
                    if pd.notna(row['告示番号']):
                        disease_data['overview'] = f"告示番号: {int(row['告示番号'])}"
                    
                    if existing:
                        # 既存の疾患を更新
                        disease_id = existing.id
                        for key, value in disease_data.items():
                            setattr(existing, key, value)
                    else:
                        # 新規作成
                        disease_id = str(uuid.uuid4())
                        disease_data['id'] = disease_id
                        new_disease = Disease(**disease_data)
                        db.add(new_disease)
                    
                    # 類義語の処理
                    self._update_synonyms(db, disease_id, row)
                    
                    # 検索キーワードの生成と保存
                    search_keywords = self._generate_search_keywords(name_ja, name_en, row)
                    
                    if existing:
                        existing.search_keywords = json.dumps(search_keywords)
                    else:
                        new_disease.search_keywords = json.dumps(search_keywords)
                    
                    imported_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {index}: {str(e)}")
                    continue
            
            db.commit()
            
            return {
                "status": "success",
                "imported": imported_count,
                "errors": error_count,
                "error_details": errors[:10] if errors else []
            }
            
        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _update_synonyms(self, db: Session, disease_id: str, row):
        """類義語を更新"""
        # 既存の類義語を削除
        db.query(DiseaseSynonym).filter(DiseaseSynonym.disease_id == disease_id).delete()
        
        # 新しい類義語を追加
        synonyms_ja = self._parse_synonyms(row['疾患名類義語（日本語）']) if pd.notna(row['疾患名類義語（日本語）']) else []
        synonyms_en = self._parse_synonyms(row['疾患名類義語（英語）']) if pd.notna(row['疾患名類義語（英語）']) else []
        
        for synonym in synonyms_ja:
            if synonym:
                new_synonym = DiseaseSynonym(
                    disease_id=disease_id,
                    synonym=synonym,
                    language='ja'
                )
                db.add(new_synonym)
        
        for synonym in synonyms_en:
            if synonym:
                new_synonym = DiseaseSynonym(
                    disease_id=disease_id,
                    synonym=synonym,
                    language='en'
                )
                db.add(new_synonym)
    
    def _generate_search_keywords(self, name_ja: str, name_en: Optional[str], row) -> List[str]:
        """検索キーワードを生成"""
        keywords = []
        
        # 基本の疾患名
        if name_ja:
            keywords.append(name_ja)
        if name_en:
            keywords.append(name_en)
        
        # 類義語を追加
        synonyms_ja = self._parse_synonyms(row['疾患名類義語（日本語）']) if pd.notna(row['疾患名類義語（日本語）']) else []
        synonyms_en = self._parse_synonyms(row['疾患名類義語（英語）']) if pd.notna(row['疾患名類義語（英語）']) else []
        
        keywords.extend(synonyms_ja)
        keywords.extend(synonyms_en)
        
        # 重複を除去
        return list(set(keywords))
    
    def _determine_disease_type(self, nando_id: str) -> str:
        """NANDOのIDから疾患タイプを判定"""
        if nando_id.startswith('NANDO:1'):
            return 'designated'
        elif nando_id.startswith('NANDO:2'):
            return 'chronic_childhood'
        else:
            return 'other'
    
    def _parse_synonyms(self, synonyms_str: str) -> List[str]:
        """類義語をパース"""
        if not synonyms_str or pd.isna(synonyms_str):
            return []
        
        synonyms = str(synonyms_str).split('|')
        return [s.strip() for s in synonyms if s.strip()]
    
    def get_disease_hierarchy(self, db: Session) -> Dict[str, Any]:
        """疾患の階層構造を取得"""
        diseases = db.query(Disease).all()
        
        hierarchy = {}
        
        for disease in diseases:
            if disease.parent_disease_id is None or disease.parent_disease_id == 'owl:Thing':
                # ルートレベルの疾患
                hierarchy[disease.nando_id] = {
                    'id': disease.id,
                    'name': disease.name,
                    'children': []
                }
        
        # 子疾患を追加
        for disease in diseases:
            if disease.parent_disease_id and disease.parent_disease_id != 'owl:Thing':
                parent = next((d for d in diseases if d.nando_id == disease.parent_disease_id), None)
                if parent and parent.nando_id in hierarchy:
                    hierarchy[parent.nando_id]['children'].append({
                        'id': disease.id,
                        'nando_id': disease.nando_id,
                        'name': disease.name
                    })
        
        return hierarchy
