"""
LangGraph共享状态定义

定义批改流水线中各Agent节点共享的State结构
"""

from typing import TypedDict, List, Dict, Any, Optional


class ErrorDetail(TypedDict):
    """错误详情"""
    type: str
    description: str


class CorrectionState(TypedDict):
    """
    批改流水线共享状态
    
    用于在LangGraph各Agent节点之间传递数据
    """
    # 作业基本信息
    homework_id: int
    image_path: str
    subject: str
    max_score: float
    
    # OCR结果
    ocr_text: str
    ocr_confidence: float
    ocr_details: List[Dict[str, Any]]
    
    # 评分结果
    score: Optional[float]
    feedback: Optional[str]
    errors: List[ErrorDetail]
    
    # 质检与流程控制
    needs_manual_review: bool
    status: str
    retry_count: int
    
    # 人工审核结果（用于恢复中断）
    manual_review_score: Optional[float]
    manual_review_feedback: Optional[str]
