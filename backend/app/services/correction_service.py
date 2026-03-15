from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.correction import Correction
from app.models.homework import Homework
from app.schemas.correction import CorrectionUpdate
import logging

logger = logging.getLogger(__name__)


class CorrectionService:
    """作业批改服务"""
    
    def auto_correct(self, db: Session, homework_id: int) -> Dict[str, Any]:
        """自动批改作业（异步），发送Celery任务"""
        logger.info(f"提交异步批改任务，作业ID: {homework_id}")
        
        homework = db.query(Homework).filter(Homework.id == homework_id).first()
        if not homework:
            raise ValueError("作业不存在")
        
        # 延迟导入，避免循环依赖
        from app.tasks.correction_task import run_correction_pipeline
        task = run_correction_pipeline.delay(homework_id)
        
        logger.info(f"批改任务已提交，任务ID: {task.id}")
        return {"task_id": task.id, "status": "processing", "homework_id": homework_id}
    
    def get_correction(self, db: Session, correction_id: int) -> Optional[Correction]:
        return db.query(Correction).filter(Correction.id == correction_id).first()
    
    def get_correction_by_homework(self, db: Session, homework_id: int) -> Optional[Correction]:
        return db.query(Correction).filter(Correction.homework_id == homework_id).first()
    
    def update_correction(self, db: Session, correction_id: int, update_data: CorrectionUpdate) -> Correction:
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
