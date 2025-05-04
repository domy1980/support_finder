from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Disease(Base):
    __tablename__ = "diseases"

    id = Column(String, primary_key=True, index=True)
    nando_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    name_kana = Column(String)
    name_en = Column(String)
    overview = Column(Text)
    characteristics = Column(Text)
    patient_count = Column(Integer)
    search_keywords = Column(Text)  # JSON形式で保存
    
    disease_type = Column(String)
    parent_disease_id = Column(String)
    is_designated_intractable = Column(Boolean, default=False)
    is_chronic_childhood = Column(Boolean, default=False)
    is_searchable = Column(Boolean, default=True)  # 新しく追加
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    organizations = relationship("Organization", back_populates="disease")
    synonyms = relationship("DiseaseSynonym", back_populates="disease")
    custom_keywords = relationship("DiseaseCustomKeyword", back_populates="disease")

class DiseaseSynonym(Base):
    __tablename__ = "disease_synonyms"
    
    id = Column(Integer, primary_key=True)
    disease_id = Column(String, ForeignKey("diseases.id"), nullable=False)
    synonym = Column(String, nullable=False)
    language = Column(String, default="ja")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    disease = relationship("Disease", back_populates="synonyms")

class DiseaseCustomKeyword(Base):
    __tablename__ = "disease_custom_keywords"
    
    id = Column(Integer, primary_key=True)
    disease_id = Column(String, ForeignKey("diseases.id"), nullable=False)
    keyword = Column(String, nullable=False)
    keyword_type = Column(String)
    added_by = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    disease = relationship("Disease", back_populates="custom_keywords")
