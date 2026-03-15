from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class ManualReview(Base):
    __tablename__ = "manual_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    correction_id = Column(Integer, ForeignKey("corrections.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 审核结果
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    review_notes = Column(Text, nullable=True)  # 审核备注
    
    # 状态
    status = Column(String, default="pending")  # pending, approved, rejected
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    correction = relationship("Correction", back_populates="manual_review")
    reviewer = relationship("User")
