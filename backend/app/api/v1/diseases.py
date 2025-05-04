from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.disease_service import DiseaseService
from app.services.keyword_service import KeywordService
from app.services.disease_hierarchy_service import DiseaseHierarchyService
from app.schemas.disease import (
    Disease, 
    DiseaseCreate, 
    DiseaseUpdate, 
    DiseaseSearchableUpdate,
    CustomKeywordCreate,
    DiseaseWithHierarchy
)
import os
import shutil
from pathlib import Path
import pandas as pd
import uuid

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

@router.get("/searchable", response_model=List[Disease])
def get_searchable_diseases(db: Session = Depends(get_db)):
    """検索対象の疾患のみを取得（is_searchable=True）"""
    diseases = disease_service.get_searchable_diseases(db)
    return diseases

@router.get("/searchable/export")
def export_searchable_diseases(db: Session = Depends(get_db)):
    """検索対象の疾患をExcelファイルとしてエクスポート"""
    diseases = disease_service.get_all_diseases_with_searchable_status(db)
    
    # データフレームを作成
    data = []
    for disease in diseases:
        data.append({
            'NANDO': disease.nando_id or '',
            'label': disease.name,
            'is_searchable': '1' if disease.is_searchable else '0'
        })
    
    df = pd.DataFrame(data)
    
    # 一時ファイルとして保存
    filename = f"searchable_diseases_{uuid.uuid4().hex[:8]}.xlsx"
    temp_file = Path(f"/tmp/{filename}")
    df.to_excel(temp_file, index=False)
    
    return FileResponse(
        path=str(temp_file),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.post("/searchable/import")
async def import_searchable_settings(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """検索対象設定をインポート"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Excel file required")
    
    # 一時ファイルとして保存
    temp_file = Path(f"temp_{file.filename}")
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Excelファイルを読み込む
        df = pd.read_excel(temp_file)
        
        # 必要なカラムが存在するか確認
        if 'is_searchable' not in df.columns:
            raise HTTPException(status_code=400, detail="is_searchable column is required")
        
        # 更新処理
        updated_count = 0
        for index, row in df.iterrows():
            nando_id = str(row['NANDO']).strip() if pd.notna(row['NANDO']) else None
            disease_name = str(row['label']).strip() if pd.notna(row['label']) else None
            is_searchable = str(row['is_searchable']) == '1'
            
            # 疾患を検索
            disease = None
            if nando_id:
                disease = db.query(Disease).filter(Disease.nando_id == nando_id).first()
            elif disease_name:
                disease = db.query(Disease).filter(Disease.name == disease_name).first()
            
            if disease:
                disease.is_searchable = is_searchable
                updated_count += 1
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"{updated_count}件の疾患の検索対象設定を更新しました。"
        }
    
    finally:
        # 一時ファイルを削除
        if temp_file.exists():
            os.remove(temp_file)

@router.get("/hierarchy/stats")
def get_hierarchy_stats(db: Session = Depends(get_db)):
    """疾患階層の統計情報を取得"""
    stats = hierarchy_service.get_disease_hierarchy_stats(db)
    return stats

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

@router.patch("/{disease_id}/searchable")
def update_disease_searchable(
    disease_id: str, 
    is_searchable: bool,
    db: Session = Depends(get_db)
):
    """疾患の検索対象フラグを更新"""
    disease = disease_service.update_disease_searchable(db, disease_id, is_searchable)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return disease

@router.post("/batch-update-searchable")
def batch_update_searchable(
    updates: List[DiseaseSearchableUpdate], 
    db: Session = Depends(get_db)
):
    """複数の疾患の検索対象フラグを一括更新"""
    updated_count = disease_service.batch_update_searchable(db, updates)
    return {"message": f"Updated {updated_count} diseases"}

# 以下、キーワード関連のエンドポイントは省略...
