"""
Celery应用配置

配置Celery实例，使用Redis作为消息队列
"""

from celery import Celery
from app.core.config import settings

# 创建Celery应用实例
celery_app = Celery(
    "k12_education",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.correction_task"]
)

# Celery配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    # 结果序列化
    result_serializer="json",
    # 接受的内容类型
    accept_content=["json"],
    # 时区设置
    timezone="Asia/Shanghai",
    # 启用UTC
    enable_utc=True,
    # 任务结果过期时间（秒）
    result_expires=3600,
    # 任务执行超时时间（秒）
    task_time_limit=300,
    # 任务软超时时间（秒）
    task_soft_time_limit=240,
    # Worker并发数
    worker_concurrency=4,
    # 每个Worker最多处理的任务数
    worker_max_tasks_per_child=100,
)

# 自动发现任务
celery_app.autodiscover_tasks()
