from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str
    url: Optional[str] = None
    description: Optional[str] = None
    contact: Optional[str] = None
    type: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    disease_id: str
    source_url: Optional[str] = None
    relevance_score: Optional[float] = None

class OrganizationUpdate(OrganizationBase):
    verification_status: Optional[str] = None
    relevance_score: Optional[float] = None

class Organization(OrganizationBase):
    id: str
    disease_id: str
    verification_status: str
    relevance_score: Optional[float] = None
    source_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
