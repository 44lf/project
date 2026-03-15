from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ManualReviewBase(BaseModel):
    score: Optional[float] = None
    feedback: Optional[str] = None
    review_notes: Optional[str] = None


class ManualReviewSubmit(BaseModel):
    """前端提交人工审核时使用（只含审核内容字段）"""
    score: Optional[float] = None
    feedback: Optional[str] = None
    review_notes: Optional[str] = None


class ManualReviewCreate(ManualReviewBase):
    """内部创建审核记录时使用的完整schema"""
    correction_id: int
    reviewer_id: int


class ManualReviewUpdate(BaseModel):
    score: Optional[float] = None
    feedback: Optional[str] = None
    review_notes: Optional[str] = None
    status: Optional[str] = None


class ManualReview(ManualReviewBase):
    id: int
    correction_id: int
    reviewer_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
