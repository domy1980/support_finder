from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.disease import DiseaseCustomKeyword
from app.schemas.disease import CustomKeywordCreate

class KeywordService:
    def __init__(self):
        pass
    
    def add_keyword(self, db: Session, disease_id: str, keyword_data: CustomKeywordCreate) -> DiseaseCustomKeyword:
        db_keyword = DiseaseCustomKeyword(
            disease_id=disease_id,
            keyword=keyword_data.keyword,
            keyword_type=keyword_data.keyword_type,
            added_by=keyword_data.added_by
        )
        db.add(db_keyword)
        db.commit()
        db.refresh(db_keyword)
        return db_keyword
    
    def get_keywords(self, db: Session, disease_id: str) -> List[DiseaseCustomKeyword]:
        return db.query(DiseaseCustomKeyword).filter(DiseaseCustomKeyword.disease_id == disease_id).all()
    
    def delete_keyword(self, db: Session, keyword_id: int) -> bool:
        keyword = db.query(DiseaseCustomKeyword).filter(DiseaseCustomKeyword.id == keyword_id).first()
        if keyword:
            db.delete(keyword)
            db.commit()
            return True
        return False
