from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.disease import Disease, DiseaseCreate, DiseaseUpdate, CustomKeywordCreate, DiseaseWithHierarchy
from app.services.disease_service import DiseaseService
from app.services.keyword_service import KeywordService
from app.services.disease_hierarchy_service import DiseaseHierarchyService
import os
import shutil
from pathlib import Path

router = APIRouter()
disease_service = DiseaseService()
keyword_service = KeywordService()
hierarchy_service = DiseaseHierarchyService()

@router.post("/", response_model=Disease)
def create_disease(disease: DiseaseCreate, db: Session = Depends(get_db)):
    return disease_service.create_disease(db, disease)

@router.get("/", response_model=List[Disease])
def list_diseases(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    diseases = disease_service.get_diseases(db, skip=skip, limit=limit)
    return diseases

@router.get("/{disease_id}", response_model=Disease)
def get_disease(disease_id: str, db: Session = Depends(get_db)):
    disease = disease_service.get_disease(db, disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return disease

@router.get("/{disease_id}/hierarchy")
def get_disease_hierarchy(disease_id: str, db: Session = Depends(get_db)):
    """疾患の階層情報を取得"""
    hierarchy_info = hierarchy_service.get_disease_hierarchy_info(db, disease_id)
    if not hierarchy_info:
        raise HTTPException(status_code=404, detail="Disease not found")
    return hierarchy_info

@router.put("/{disease_id}", response_model=Disease)
def update_disease(disease_id: str, disease: DiseaseUpdate, db: Session = Depends(get_db)):
    updated_disease = disease_service.update_disease(db, disease_id, disease)
    if not updated_disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return updated_disease

@router.delete("/{disease_id}")
def delete_disease(disease_id: str, db: Session = Depends(get_db)):
    success = disease_service.delete_disease(db, disease_id)
    if not success:
        raise HTTPException(status_code=404, detail="Disease not found")
    return {"message": "Disease deleted successfully"}

@router.get("/search/{query}", response_model=List[Disease])
def search_diseases(query: str, db: Session = Depends(get_db)):
    return disease_service.search_diseases(db, query)

@router.get("/searchable", response_model=List[Disease])
def get_searchable_diseases(db: Session = Depends(get_db)):
    """検索すべき疾患のリストを取得"""
    searchable_diseases = hierarchy_service.get_searchable_diseases(db)
    return searchable_diseases

@router.get("/hierarchy/stats")
def get_hierarchy_stats(db: Session = Depends(get_db)):
    """疾患階層の統計情報を取得"""
    stats = hierarchy_service.get_disease_hierarchy_stats(db)
    return stats

# カスタムキーワード関連のエンドポイント...
