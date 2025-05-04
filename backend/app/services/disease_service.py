from typing import List, Optional
import json
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.disease import Disease
from app.schemas.disease import DiseaseCreate, DiseaseUpdate, DiseaseSearchableUpdate

class DiseaseService:
    def create_disease(self, db: Session, disease: DiseaseCreate) -> Disease:
        # search_keywordsをJSON文字列に変換
        search_keywords_json = json.dumps(disease.search_keywords) if disease.search_keywords else None
        
        db_disease = Disease(
            id=disease.id,
            nando_id=disease.nando_id,
            name=disease.name,
            name_kana=disease.name_kana,
            name_en=disease.name_en,
            overview=disease.overview,
            characteristics=disease.characteristics,
            patient_count=disease.patient_count,
            search_keywords=search_keywords_json,
            disease_type=disease.disease_type,
            parent_disease_id=disease.parent_disease_id,
            is_designated_intractable=disease.is_designated_intractable,
            is_chronic_childhood=disease.is_chronic_childhood,
            is_searchable=disease.is_searchable if hasattr(disease, 'is_searchable') else True
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

    def get_searchable_diseases(self, db: Session) -> List[Disease]:
        """検索対象の疾患のみを取得"""
        return db.query(Disease).filter(Disease.is_searchable == True).all()

    def update_disease_searchable(self, db: Session, disease_id: str, is_searchable: bool) -> Optional[Disease]:
        """疾患の検索対象フラグを更新"""
        disease = self.get_disease(db, disease_id)
        if not disease:
            return None
        
        disease.is_searchable = is_searchable
        db.commit()
        db.refresh(disease)
        return disease

    def batch_update_searchable(self, db: Session, updates: List[DiseaseSearchableUpdate]) -> int:
        """複数の疾患の検索対象フラグを一括更新"""
        updated_count = 0
        for update in updates:
            disease = self.get_disease(db, update.disease_id)
            if disease:
                disease.is_searchable = update.is_searchable
                updated_count += 1
        
        if updated_count > 0:
            db.commit()
        return updated_count

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

    def get_all_diseases_with_searchable_status(self, db: Session) -> List[Disease]:
        """全疾患を検索対象フラグ付きで取得"""
        return db.query(Disease).order_by(Disease.nando_id).all()
