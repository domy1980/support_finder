from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.nando_import_service import NandoImportService
from app.services.scheduled_search_service import ScheduledSearchService
import shutil
import os
from pathlib import Path
import asyncio

router = APIRouter()

@router.post("/import")
async def import_nando_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """NANDOデータファイルをインポート"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Excel file required")
    
    # 一時ファイルとして保存
    temp_file = Path(f"temp_{file.filename}")
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # インポート実行
        import_service = NandoImportService()
        result = import_service.import_nando_data(db, str(temp_file))
        
        return result
    
    finally:
        # 一時ファイルを削除
        if temp_file.exists():
            os.remove(temp_file)

@router.get("/hierarchy")
async def get_disease_hierarchy(db: Session = Depends(get_db)):
    """疾患の階層構造を取得"""
    import_service = NandoImportService()
    hierarchy = import_service.get_disease_hierarchy(db)
    return hierarchy

@router.post("/search/comprehensive")
async def run_comprehensive_search(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """全疾患の包括的な検索を開始（バックグラウンドで実行）"""
    
    async def search_task():
        search_service = ScheduledSearchService()
        await search_service.run_comprehensive_search(db)
    
    background_tasks.add_task(search_task)
    
    return {
        "message": "Comprehensive search started in background",
        "status": "processing"
    }
