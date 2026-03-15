"""
批改任务

定义作业批改的异步Celery任务
"""

import logging
from typing import Dict, Any

from celery import Task

from app.tasks.celery_app import celery_app
from app.agents.graph import compiled_graph
from app.agents.state import CorrectionState
from app.db.database import SessionLocal
from app.models.homework import Homework

logger = logging.getLogger(__name__)


class CorrectionTask(Task):
    """
    批改任务基类
    
    提供数据库会话管理等通用功能
    """
    
    _db = None
    
    def after_return(self, *args, **kwargs):
        """任务完成后关闭数据库连接"""
        if self._db:
            self._db.close()
            self._db = None


@celery_app.task(
    bind=True,
    base=CorrectionTask,
    max_retries=3,
    default_retry_delay=60,
    time_limit=300,
    soft_time_limit=240
)
def run_correction_pipeline(self, homework_id: int) -> Dict[str, Any]:
    """
    运行批改流水线任务
    
    从数据库读取作业信息，构造初始状态，调用LangGraph执行批改流程
    
    Args:
        self: Celery任务实例
        homework_id: 作业ID
        
    Returns:
        包含执行结果的字典
        
    Raises:
        失败时会自动重试，最多3次
    """
    logger.info(f"开始执行批改任务，作业ID: {homework_id}")
    
    db = SessionLocal()
    try:
        # 从数据库读取作业信息
        homework = db.query(Homework).filter(Homework.id == homework_id).first()
        
        if not homework:
            logger.error(f"作业不存在，ID: {homework_id}")
            return {
                "success": False,
                "error": "作业不存在",
                "homework_id": homework_id
            }
        
        # 更新作业状态为处理中
        homework.status = "processing"
        db.commit()
        
        # 构造初始状态
        initial_state: CorrectionState = {
            "homework_id": homework_id,
            "image_path": homework.file_path,
            "subject": homework.subject,
            "max_score": 100.0,
            "ocr_text": "",
            "ocr_confidence": 0.0,
            "ocr_details": [],
            "score": None,
            "feedback": None,
            "errors": [],
            "needs_manual_review": False,
            "status": "started",
            "retry_count": self.request.retries,
            "manual_review_score": None,
            "manual_review_feedback": None
        }
        
        logger.info(f"调用LangGraph执行批改，作业ID: {homework_id}")
        
        # 调用LangGraph执行批改流程
        result = compiled_graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": str(homework_id)}}
        )
        
        # 检查结果
        final_status = result.get("status", "unknown")
        needs_review = result.get("needs_manual_review", False)
        
        logger.info(
            f"批改任务完成，作业ID: {homework_id}, "
            f"状态: {final_status}, 需要人工审核: {needs_review}"
        )
        
        return {
            "success": True,
            "homework_id": homework_id,
            "status": final_status,
            "needs_manual_review": needs_review,
            "score": result.get("score"),
            "feedback": result.get("feedback"),
            "ocr_confidence": result.get("ocr_confidence")
        }
        
    except Exception as e:
        logger.exception(f"批改任务执行失败，作业ID: {homework_id}, 错误: {str(e)}")
        
        # 更新作业状态为失败
        try:
            homework = db.query(Homework).filter(Homework.id == homework_id).first()
            if homework:
                homework.status = "failed"
                db.commit()
        except Exception as db_error:
            logger.error(f"更新作业状态失败: {str(db_error)}")
        
        # 如果还有重试次数，则重试
        if self.request.retries < self.max_retries:
            logger.info(f"任务将在{self.default_retry_delay}秒后重试，当前重试次数: {self.request.retries}")
            raise self.retry(exc=e)
        
        # 重试次数用尽，返回失败结果
        return {
            "success": False,
            "error": str(e),
            "homework_id": homework_id,
            "retries": self.request.retries
        }
        
    finally:
        db.close()
