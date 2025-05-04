from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.llm_service import LLMService

router = APIRouter()

class TestExtractionRequest(BaseModel):
    text: str
    disease_name: str

@router.get("/health")
async def check_llm_health():
    """LLMサービスの健康状態を確認"""
    llm_service = LLMService()
    is_healthy = await llm_service.check_health()
    return {"status": "healthy" if is_healthy else "unhealthy"}

@router.get("/models")
async def get_available_models():
    """利用可能なモデルの一覧を取得"""
    llm_service = LLMService()
    models = await llm_service.get_available_models()
    return {"models": models}

@router.post("/test-extraction")
async def test_extraction(request: TestExtractionRequest):
    """テキストから組織情報を抽出するテスト"""
    llm_service = LLMService()
    try:
        result = await llm_service.extract_organization_info(
            request.text, 
            request.disease_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
