"""
质检Agent节点

负责检查OCR和评分结果质量，决定是否需要人工审核
"""

import logging
from typing import Dict, Any

from app.agents.state import CorrectionState
from app.core.config import settings

logger = logging.getLogger(__name__)


def quality_agent(state: CorrectionState) -> Dict[str, Any]:
    """
    质检Agent节点
    
    检查OCR置信度、评分结果等，决定是否需要转人工审核
    
    检查规则：
    1. OCR置信度 < MANUAL_REVIEW_THRESHOLD(0.70) → 需要人工审核
    2. 评分异常（score为None或<0或>100） → 需要人工审核
    3. LLM返回解析失败 → 需要人工审核
    
    Args:
        state: 当前流水线状态
        
    Returns:
        包含needs_manual_review和status的字典
    """
    logger.info(f"开始质量检查，作业ID: {state['homework_id']}")
    
    needs_manual_review = False
    review_reasons = []
    
    try:
        # 检查1: OCR置信度
        ocr_confidence = state.get("ocr_confidence", 0)
        if ocr_confidence < settings.MANUAL_REVIEW_THRESHOLD:
            needs_manual_review = True
            review_reasons.append(f"OCR置信度过低({ocr_confidence:.2f} < {settings.MANUAL_REVIEW_THRESHOLD})")
            logger.warning(f"OCR置信度不足: {ocr_confidence:.4f}")
        
        # 检查2: 评分结果有效性
        score = state.get("score")
        if score is None:
            needs_manual_review = True
            review_reasons.append("评分结果为None")
            logger.warning("评分结果为None")
        elif score < 0 or score > 100:
            needs_manual_review = True
            review_reasons.append(f"评分异常({score})")
            logger.warning(f"评分异常: {score}")
        
        # 检查3: 前置流程失败
        current_status = state.get("status", "")
        if current_status in ["ocr_failed", "scoring_failed"]:
            needs_manual_review = True
            review_reasons.append(f"前置流程失败({current_status})")
            logger.warning(f"前置流程失败: {current_status}")
        
        # 检查4: OCR文本为空或过短
        ocr_text = state.get("ocr_text", "")
        if not ocr_text or len(ocr_text.strip()) < 5:
            needs_manual_review = True
            review_reasons.append("OCR文本为空或过短")
            logger.warning("OCR文本为空或过短")
        
        # 确定最终状态
        if needs_manual_review:
            status = "needs_manual_review"
            logger.info(f"需要人工审核，原因: {'; '.join(review_reasons)}")
        else:
            status = "quality_passed"
            logger.info("质量检查通过")
        
        return {
            "needs_manual_review": needs_manual_review,
            "status": status
        }
        
    except Exception as e:
        logger.exception(f"质量检查异常: {str(e)}")
        # 异常情况下也转人工审核
        return {
            "needs_manual_review": True,
            "status": "quality_check_failed"
        }
