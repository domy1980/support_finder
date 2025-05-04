from typing import List, Dict, Any
import json
from sqlalchemy.orm import Session
from app.models.disease import Disease, DiseaseCustomKeyword
from app.schemas.disease import CustomKeywordCreate

class KeywordService:
    def add_custom_keyword(self, db: Session, disease_id: str, keyword_data: CustomKeywordCreate) -> DiseaseCustomKeyword:
        """カスタムキーワードを追加"""
        custom_keyword = DiseaseCustomKeyword(
            disease_id=disease_id,
            keyword=keyword_data.keyword,
            keyword_type=keyword_data.keyword_type,
            added_by=keyword_data.added_by
        )
        db.add(custom_keyword)
        
        # 疾患の検索キーワードを更新
        self._update_disease_search_keywords(db, disease_id)
        
        db.commit()
        db.refresh(custom_keyword)
        return custom_keyword
    
    def remove_custom_keyword(self, db: Session, keyword_id: int) -> bool:
        """カスタムキーワードを削除"""
        keyword = db.query(DiseaseCustomKeyword).filter(DiseaseCustomKeyword.id == keyword_id).first()
        if not keyword:
            return False
        
        disease_id = keyword.disease_id
        db.delete(keyword)
        
        # 疾患の検索キーワードを更新
        self._update_disease_search_keywords(db, disease_id)
        
        db.commit()
        return True
    
    def get_custom_keywords(self, db: Session, disease_id: str) -> List[DiseaseCustomKeyword]:
        """疾患のカスタムキーワードを取得"""
        return db.query(DiseaseCustomKeyword).filter(DiseaseCustomKeyword.disease_id == disease_id).all()
    
    def import_keywords_from_csv(self, db: Session, file_path: str) -> Dict[str, Any]:
        """CSVファイルからキーワードを一括インポート"""
        import pandas as pd
        
        try:
            df = pd.read_csv(file_path)
            required_columns = ['disease_id', 'keyword', 'keyword_type']
            
            if not all(col in df.columns for col in required_columns):
                return {"status": "error", "message": "Required columns missing"}
            
            imported_count = 0
            
            for _, row in df.iterrows():
                disease = db.query(Disease).filter(Disease.id == row['disease_id']).first()
                if disease:
                    keyword_data = CustomKeywordCreate(
                        keyword=row['keyword'],
                        keyword_type=row.get('keyword_type', 'other'),
                        added_by='table_import'
                    )
                    self.add_custom_keyword(db, disease.id, keyword_data)
                    imported_count += 1
            
            return {"status": "success", "imported": imported_count}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _update_disease_search_keywords(self, db: Session, disease_id: str):
        """疾患の検索キーワードを更新"""
        disease = db.query(Disease).filter(Disease.id == disease_id).first()
        if not disease:
            return
        
        # 基本キーワード
        keywords = []
        if disease.name:
            keywords.append(disease.name)
        if disease.name_en:
            keywords.append(disease.name_en)
        
        # 類義語を追加
        synonyms = disease.synonyms
        for synonym in synonyms:
            keywords.append(synonym.synonym)
        
        # カスタムキーワードを追加
        custom_keywords = disease.custom_keywords
        for custom in custom_keywords:
            keywords.append(custom.keyword)
        
        # 重複を除去して保存
        unique_keywords = list(set(keywords))
        disease.search_keywords = json.dumps(unique_keywords)
        db.commit()
