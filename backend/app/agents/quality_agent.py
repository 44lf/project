"""
质检Agent节点

负责检查OCR和评分结果质量，决定是否需要人工审核。
当需要人工审核时，在此节点内创建待审核记录（因为后续的human_review节点会被interrupt_before中断，不会执行）。
"""

import logging
from typing import Dict, Any

from app.agents.state import CorrectionState
from app.core.config import settings
from app.db.database import SessionLocal
from app.models.correction import Correction
from app.models.homework import Homework

logger = logging.getLogger(__name__)


def _create_pending_review_record(state: CorrectionState) -> None:
    """
    创建待审核记录
    
    当质检判定需要人工审核时，在quality_agent节点内创建/更新Correction记录。
    这是因为human_review节点会被interrupt_before中断，其代码不会执行。
    
    Args:
        state: 当前流水线状态
    """
    db = SessionLocal()
    try:
        homework_id = state["homework_id"]
        logger.info(f"创建待审核记录，作业ID: {homework_id}")
        
        # 检查是否已存在该作业的Correction记录
        existing_correction = db.query(Correction).filter(
            Correction.homework_id == homework_id
        ).first()
        
        if existing_correction:
            # 更新现有记录为待审核状态
            existing_correction.ocr_text = state.get("ocr_text")
            existing_correction.ocr_confidence = state.get("ocr_confidence")
            existing_correction.ocr_details = state.get("ocr_details")
            existing_correction.score = state.get("score")
            existing_correction.feedback = state.get("feedback")
            existing_correction.errors = state.get("errors", [])
            existing_correction.status = "pending_review"
            existing_correction.needs_manual_review = 1
            logger.info(f"更新现有Correction记录为待审核状态，ID: {existing_correction.id}")
        else:
            # 创建新的待审核记录
            correction = Correction(
                homework_id=homework_id,
                ocr_text=state.get("ocr_text"),
                ocr_confidence=state.get("ocr_confidence"),
                ocr_details=state.get("ocr_details"),
                score=state.get("score"),
                feedback=state.get("feedback"),
                errors=state.get("errors", []),
                status="pending_review",
                needs_manual_review=1
            )
            db.add(correction)
            logger.info(f"创建新Correction待审核记录")
        
        # 更新Homework状态为审核中
        homework = db.query(Homework).filter(Homework.id == homework_id).first()
        if homework:
            homework.status = "reviewing"
            logger.info(f"更新作业状态为reviewing，作业ID: {homework_id}")
        
        db.commit()
        logger.info(f"待审核记录创建/更新成功，作业ID: {homework_id}")
        
    except Exception as e:
        logger.exception(f"创建待审核记录失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


def quality_agent(state: CorrectionState) -> Dict[str, Any]:
    """
    质检Agent节点
    
    检查OCR置信度、评分结果等，决定是否需要转人工审核。
    如果需要人工审核，在此处创建待审核的Correction记录和更新Homework状态，
    因为后续的human_review节点会被interrupt_before中断，其代码不会执行。
    
    检查规则：
    1. OCR置信度 < MANUAL_REVIEW_THRESHOLD(0.70) → 需要人工审核
    2. 评分异常（score为None或<0或>100） → 需要人工审核
    3. LLM返回解析失败（前置流程失败） → 需要人工审核
    4. OCR文本为空或过短 → 需要人工审核
    
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
            # 关键：在此处创建待审核记录（因为human_review节点会被中断）
            _create_pending_review_record(state)
        else:
            status = "quality_passed"
            logger.info("质量检查通过")
        
        return {
            "needs_manual_review": needs_manual_review,
            "status": status
        }
        
    except Exception as e:
        logger.exception(f"质量检查异常: {str(e)}")
        # 异常情况下也转人工审核，并创建记录
        _create_pending_review_record(state)
        return {
            "needs_manual_review": True,
            "status": "quality_check_failed"
        }
