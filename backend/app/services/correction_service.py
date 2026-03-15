from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.correction import Correction
from app.models.homework import Homework
from app.schemas.correction import CorrectionCreate, CorrectionUpdate
from app.services.ocr_service import ocr_service
from app.core.config import settings
from app.tasks.correction_task import run_correction_pipeline

import logging

logger = logging.getLogger(__name__)


class CorrectionService:
    """作业批改服务"""
    
    def __init__(self):
        self.ocr = ocr_service
    
    def auto_correct(self, db: Session, homework_id: int) -> Dict[str, Any]:
        """
        自动批改作业（异步）
        
        发送Celery异步任务执行批改流水线，不再同步执行批改逻辑
        
        Args:
            db: 数据库会话
            homework_id: 作业ID
            
        Returns:
            包含任务ID和状态的字典
        """
        logger.info(f"提交异步批改任务，作业ID: {homework_id}")
        
        # 获取作业信息
        homework = db.query(Homework).filter(Homework.id == homework_id).first()
        if not homework:
            raise ValueError("作业不存在")
        
        # 发送Celery异步任务
        task = run_correction_pipeline.delay(homework_id)
        
        logger.info(f"批改任务已提交，作业ID: {homework_id}, 任务ID: {task.id}")
        
        return {
            "task_id": task.id,
            "status": "processing",
            "homework_id": homework_id,
            "message": "批改任务已提交，正在异步处理中"
        }
    
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
