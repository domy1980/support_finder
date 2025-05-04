from typing import List, Dict, Any
import uuid
from sqlalchemy.orm import Session
from app.services.disease_service import DiseaseService
from app.services.llm_service import LLMService
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate

class SearchService:
    def __init__(self):
        self.disease_service = DiseaseService()
        self.llm_service = LLMService()
    
    async def generate_search_terms(self, disease_name: str, disease_name_en: str = None) -> List[str]:
        """検索語を生成"""
        search_terms = []
        
        # 基本的な検索語
        if disease_name:
            search_terms.append(f"{disease_name} 患者会")
            search_terms.append(f"{disease_name} 家族会")
            search_terms.append(f"{disease_name} 支援団体")
        
        if disease_name_en:
            search_terms.append(f"{disease_name_en} patient association")
            search_terms.append(f"{disease_name_en} support group")
        
        return search_terms
    
    async def search_organizations(self, db: Session, disease_id: str) -> List[Dict[str, Any]]:
        """疾患に関連する組織を検索（簡易版）"""
        disease = self.disease_service.get_disease(db, disease_id)
        if not disease:
            return []
        
        # テスト用のダミーデータ
        dummy_organizations = [
            {
                'name': '日本ALS協会',
                'url': 'https://www.alsjapan.org/',
                'description': '筋萎縮性側索硬化症（ALS）の患者とその家族を支援する団体です。',
                'contact': 'info@alsjapan.org',
                'type': 'patient'
            },
            {
                'name': 'ALS患者・家族支援センター',
                'url': 'https://example.com/als-support',
                'description': 'ALS患者と家族のための相談・支援を行っています。',
                'contact': '03-1234-5678',
                'type': 'support'
            }
        ]
        
        all_organizations = []
        
        for org in dummy_organizations:
            org_data = OrganizationCreate(
                disease_id=disease_id,
                name=org['name'],
                url=org['url'],
                description=org['description'],
                contact=org['contact'],
                type=org['type'],
                source_url=org['url'],
                relevance_score=95.0
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
        
        db.commit()
        return all_organizations
