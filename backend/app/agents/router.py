"""
条件路由函数

根据质检结果决定流程走向
"""

import logging

from app.agents.state import CorrectionState

logger = logging.getLogger(__name__)


def route_after_quality(state: CorrectionState) -> str:
    """
    质检后的条件路由函数
    
    根据needs_manual_review字段决定流程走向：
    - 如果需要人工审核 → 返回 "human_review"
    - 如果不需要 → 返回 "save_result"
    
    Args:
        state: 当前流水线状态
        
    Returns:
        下一个节点的名称字符串
    """
    needs_manual_review = state.get("needs_manual_review", False)
    
    if needs_manual_review:
        logger.info(f"作业ID {state['homework_id']} 路由到人工审核节点")
        return "human_review"
    else:
        logger.info(f"作业ID {state['homework_id']} 路由到保存结果节点")
        return "save_result"
