from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Correction(Base):
    __tablename__ = "corrections"
    
    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homeworks.id"), nullable=False)
    
    # OCR结果
    ocr_text = Column(Text, nullable=True)  # 识别的文本内容
    ocr_confidence = Column(Float, nullable=True)  # OCR平均置信度
    ocr_details = Column(JSON, nullable=True)  # 详细OCR结果（每个字符的置信度等）
    
    # 批改结果
    score = Column(Float, nullable=True)  # 得分
    max_score = Column(Float, default=100)  # 满分
    feedback = Column(Text, nullable=True)  # 评语
    errors = Column(JSON, nullable=True)  # 错误详情
    
    # 状态
    status = Column(String, default="pending")  # pending, auto_corrected, manual_reviewed
    needs_manual_review = Column(Integer, default=0)  # 是否需要人工审核
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    homework = relationship("Homework", back_populates="correction")
    manual_review = relationship("ManualReview", back_populates="correction", uselist=False)
