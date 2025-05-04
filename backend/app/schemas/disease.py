from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict
from datetime import datetime
import json

class DiseaseHierarchyInfo(BaseModel):
    id: str
    name: str
    nando_id: Optional[str] = None

class DiseaseBase(BaseModel):
    name: str
    name_kana: Optional[str] = None
    name_en: Optional[str] = None
    overview: Optional[str] = None
    characteristics: Optional[str] = None
    patient_count: Optional[int] = None
    search_keywords: Optional[List[str]] = None

class DiseaseCreate(DiseaseBase):
    id: str
    nando_id: Optional[str] = None
    disease_type: Optional[str] = None
    parent_disease_id: Optional[str] = None
    is_designated_intractable: bool = False
    is_chronic_childhood: bool = False

class DiseaseUpdate(BaseModel):
    name: Optional[str] = None
    name_kana: Optional[str] = None
    name_en: Optional[str] = None
    overview: Optional[str] = None
    characteristics: Optional[str] = None
    patient_count: Optional[int] = None
    search_keywords: Optional[List[str]] = None

class CustomKeywordCreate(BaseModel):
    keyword: str
    keyword_type: Optional[str] = 'other'  # 'symptom', 'treatment', 'other'
    added_by: Optional[str] = 'manual'

class Disease(DiseaseBase):
    id: str
    nando_id: Optional[str] = None
    disease_type: Optional[str] = None
    parent_disease_id: Optional[str] = None
    is_designated_intractable: bool
    is_chronic_childhood: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('search_keywords', mode='before')
    @classmethod
    def parse_search_keywords(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return None
        return v

    class Config:
        from_attributes = True

class DiseaseWithHierarchy(Disease):
    parent: Optional[DiseaseHierarchyInfo] = None
    children: List[DiseaseHierarchyInfo] = []
