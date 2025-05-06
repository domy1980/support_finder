from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.services.search_service_google import GoogleSearchService

router = APIRouter()
search_service = GoogleSearchService()

@router.post("/disease/{disease_id}")
async def search_organizations_for_disease(
    disease_id: str,
    db: Session = Depends(get_db)
):
    """特定の疾患に関連する組織を検索"""
    try:
        organizations = await search_service.search_organizations(db, disease_id)
        return {
            "disease_id": disease_id,
            "organizations": organizations,
            "count": len(organizations)
        }
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/terms/{disease_id}")
async def get_search_terms(disease_id: str, db: Session = Depends(get_db)):
    """検索語の一覧を取得"""
    disease = search_service.disease_service.get_disease(db, disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    
    terms = await search_service.generate_search_terms(disease.name, disease.name_en)
    return {"disease_id": disease_id, "search_terms": terms}
