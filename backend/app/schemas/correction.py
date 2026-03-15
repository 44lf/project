from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class CorrectionBase(BaseModel):
    score: Optional[float] = None
    max_score: float = 100
    feedback: Optional[str] = None


class CorrectionCreate(CorrectionBase):
    homework_id: int


class CorrectionUpdate(BaseModel):
    score: Optional[float] = None
    feedback: Optional[str] = None
    errors: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class Correction(CorrectionBase):
    id: int
    homework_id: int
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    ocr_details: Optional[Dict[str, Any]] = None
    errors: Optional[Dict[str, Any]] = None
    status: str
    needs_manual_review: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
