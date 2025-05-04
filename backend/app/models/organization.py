from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, index=True)
    disease_id = Column(String, ForeignKey("diseases.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String)
    description = Column(Text)
    contact = Column(String)
    type = Column(String)  # patient, family, support
    verification_status = Column(String, default="pending")  # pending, verified, rejected
    relevance_score = Column(Float)
    source_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    disease = relationship("Disease", back_populates="organizations")
