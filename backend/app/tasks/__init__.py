"""
Celery异步任务模块

提供作业批改的异步任务队列支持
"""

from app.tasks.celery_app import celery_app
from app.tasks.correction_task import run_correction_pipeline

__all__ = ["celery_app", "run_correction_pipeline"]
