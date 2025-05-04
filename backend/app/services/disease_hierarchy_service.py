from typing import List, Dict, Set, Optional
from sqlalchemy.orm import Session
from app.models.disease import Disease
import json
import re

class DiseaseHierarchyService:
    def __init__(self):
        pass
    
    def get_searchable_diseases(self, db: Session) -> List[Disease]:
        """検索対象の疾患を取得（手動で設定されたもののみ）"""
        return db.query(Disease).filter(Disease.is_searchable == True).all()
    
    def get_disease_hierarchy_info(self, db: Session, disease_id: str) -> Dict:
        """疾患の階層情報を取得"""
        disease = db.query(Disease).filter(Disease.id == disease_id).first()
        if not disease:
            return None
        
        # 親疾患を取得
        parent = None
        if disease.parent_disease_id and disease.parent_disease_id != 'owl:Thing':
            parent = db.query(Disease).filter(Disease.nando_id == disease.parent_disease_id).first()
        
        # 子疾患を取得
        children = db.query(Disease).filter(Disease.parent_disease_id == disease.nando_id).all()
        
        return {
            'disease': {
                'id': disease.id,
                'name': disease.name,
                'nando_id': disease.nando_id
            },
            'parent': {
                'id': parent.id,
                'name': parent.name,
                'nando_id': parent.nando_id
            } if parent else None,
            'children': [
                {
                    'id': child.id,
                    'name': child.name,
                    'nando_id': child.nando_id
                } for child in children
            ]
        }
    
    def get_disease_hierarchy_stats(self, db: Session) -> Dict:
        """疾患階層の統計情報を取得"""
        all_diseases = db.query(Disease).all()
        searchable_diseases = db.query(Disease).filter(Disease.is_searchable == True).all()
        
        return {
            'total_diseases': len(all_diseases),
            'searchable_diseases': len(searchable_diseases),
            'reduction_rate': f"{(1 - len(searchable_diseases) / len(all_diseases)) * 100:.1f}%" if all_diseases else "0%"
        }
