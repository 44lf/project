from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.correction import Correction
from app.models.homework import Homework
from app.schemas.correction import CorrectionCreate, CorrectionUpdate
from app.services.ocr_service import ocr_service
from app.core.config import settings


class CorrectionService:
    """作业批改服务"""
    
    def __init__(self):
        self.ocr = ocr_service
    
    def auto_correct(self, db: Session, homework_id: int) -> Correction:
        """自动批改作业"""
        # 获取作业信息
        homework = db.query(Homework).filter(Homework.id == homework_id).first()
        if not homework:
            raise ValueError("作业不存在")
        
        # 进行OCR识别
        ocr_result = self.ocr.recognize(homework.file_path)
        
        # 判断是否需人工审核
        needs_review = self.ocr.needs_manual_review(ocr_result.get("confidence", 0))
        
        # 简单批改逻辑（示例）
        score, feedback, errors = self._calculate_score(
            homework.subject,
            ocr_result.get("text", "")
        )
        
        # 创建批改记录
        correction = Correction(
            homework_id=homework_id,
            ocr_text=ocr_result.get("text"),
            ocr_confidence=ocr_result.get("confidence"),
            ocr_details=ocr_result.get("details"),
            score=score,
            feedback=feedback,
            errors=errors,
            status="auto_corrected" if not needs_review else "pending",
            needs_manual_review=1 if needs_review else 0
        )
        
        db.add(correction)
        db.commit()
        db.refresh(correction)
        
        # 更新作业状态
        homework.status = "completed" if not needs_review else "processing"
        db.commit()
        
        return correction
    
    def _calculate_score(self, subject: str, text: str) -> tuple:
        """
        计算得分（简化版示例）
        实际应用中应该根据学科和题目类型进行智能评分
        """
        # 这里只是一个示例逻辑
        if not text or len(text.strip()) < 10:
            return 0, "未识别到有效内容，请重新上传清晰的作业图片。", {"error": "content_too_short"}
        
        # 模拟评分逻辑
        text_length = len(text)
        base_score = min(text_length / 10, 100)  # 基于字数的基础分
        
        # 根据学科调整
        subject_bonus = {
            "math": 5,
            "chinese": 0,
            "english": 0,
            "physics": 5,
            "chemistry": 5
        }.get(subject.lower(), 0)
        
        final_score = min(base_score + subject_bonus, 100)
        
        if final_score >= 90:
            feedback = "优秀！作业完成得很好。"
        elif final_score >= 80:
            feedback = "良好，继续保持。"
        elif final_score >= 60:
            feedback = "及格，还有提升空间。"
        else:
            feedback = "需要努力，建议复习相关知识点。"
        
        errors = {
            "word_count": text_length,
            "suggestions": ["注意书写规范", "保持作业整洁"]
        }
        
        return round(final_score, 2), feedback, errors
    
    def get_correction(self, db: Session, correction_id: int) -> Optional[Correction]:
        """获取批改详情"""
        return db.query(Correction).filter(Correction.id == correction_id).first()
    
    def get_correction_by_homework(self, db: Session, homework_id: int) -> Optional[Correction]:
        """根据作业ID获取批改结果"""
        return db.query(Correction).filter(Correction.homework_id == homework_id).first()
    
    def update_correction(self, db: Session, correction_id: int, update_data: CorrectionUpdate) -> Correction:
        """更新批改结果（人工审核用）"""
        correction = self.get_correction(db, correction_id)
        if not correction:
            raise ValueError("批改记录不存在")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(correction, field, value)
        
        db.commit()
        db.refresh(correction)
        return correction


correction_service = CorrectionService()
