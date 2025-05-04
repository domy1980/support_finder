from typing import List, Optional
import json
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.disease import Disease
from app.schemas.disease import DiseaseCreate, DiseaseUpdate

class DiseaseService:
    def create_disease(self, db: Session, disease: DiseaseCreate) -> Disease:
        # search_keywordsをJSON文字列に変換
        search_keywords_json = json.dumps(disease.search_keywords) if disease.search_keywords else None
        
        db_disease = Disease(
            id=disease.id,
            name=disease.name,
            name_kana=disease.name_kana,
            name_en=disease.name_en,
            overview=disease.overview,
            patient_count=disease.patient_count,
            search_keywords=search_keywords_json
        )
        db.add(db_disease)
        db.commit()
        db.refresh(db_disease)
        return db_disease

    def get_disease(self, db: Session, disease_id: str) -> Optional[Disease]:
        disease = db.query(Disease).filter(Disease.id == disease_id).first()
        return disease

    def get_diseases(self, db: Session, skip: int = 0, limit: int = 100) -> List[Disease]:
        diseases = db.query(Disease).offset(skip).limit(limit).all()
        return diseases

    def update_disease(self, db: Session, disease_id: str, disease: DiseaseUpdate) -> Optional[Disease]:
        db_disease = self.get_disease(db, disease_id)
        if not db_disease:
            return None
        
        disease_data = disease.dict(exclude_unset=True)
        if 'search_keywords' in disease_data and disease_data['search_keywords'] is not None:
            disease_data['search_keywords'] = json.dumps(disease_data['search_keywords'])
        
        for key, value in disease_data.items():
            setattr(db_disease, key, value)
        
        db.commit()
        db.refresh(db_disease)
        return db_disease

    def delete_disease(self, db: Session, disease_id: str) -> bool:
        db_disease = self.get_disease(db, disease_id)
        if not db_disease:
            return False
        
        db.delete(db_disease)
        db.commit()
        return True

    def search_diseases(self, db: Session, query: str) -> List[Disease]:
        """疾患を検索（検索キーワードも含めて検索）"""
        search_query = f"%{query}%"
        
        # search_keywordsフィールドも検索対象に含める
        diseases = db.query(Disease).filter(
            or_(
                Disease.name.ilike(search_query),
                Disease.name_kana.ilike(search_query),
                Disease.name_en.ilike(search_query),
                Disease.search_keywords.ilike(search_query)
            )
        ).all()
        
        return diseases
