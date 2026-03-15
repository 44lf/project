"""
LangGraph StateGraph组装

构建批改流水线的状态图，包含OCR、评分、质检等节点，
支持人工审核中断和恢复机制。
"""

import json
import logging
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.state import CorrectionState
from app.agents.ocr_agent import ocr_agent
from app.agents.scoring_agent import scoring_agent
from app.agents.quality_agent import quality_agent
from app.agents.router import route_after_quality
from app.db.database import SessionLocal
from app.models.correction import Correction
from app.models.homework import Homework

logger = logging.getLogger(__name__)


def human_review_node(state: CorrectionState) -> Dict[str, Any]:
    """
    人工审核节点
    
    此节点会在执行前被中断（interrupt_before），等待教师通过API提交审核结果。
    实际的待审核记录创建已在 quality_agent 中完成，此节点仅记录日志和返回状态。
    
    当教师提交审核后，调用 resume_with_human_review() 函数：
    1. 使用 update_state() 更新状态（manual_review_score, manual_review_feedback）
    2. 使用 invoke(None) 恢复执行
    
    Args:
        state: 当前流水线状态
        
    Returns:
        包含状态的字典
    """
    logger.info(f"进入人工审核节点（已中断等待），作业ID: {state['homework_id']}")
    
    # 注意：待审核记录的创建已在 quality_agent 中完成
    # 此处仅记录日志，实际的人工审核结果会通过 resume_with_human_review 更新状态
    
    return {
        "status": "waiting_for_human_review"
    }


def save_result_node(state: CorrectionState) -> Dict[str, Any]:
    """
    保存结果节点
    
    将批改结果保存到数据库，更新作业状态
    
    Args:
        state: 当前流水线状态
        
    Returns:
        包含最终状态的字典
    """
    logger.info(f"保存批改结果，作业ID: {state['homework_id']}")
    
    db = SessionLocal()
    try:
        # 确定最终分数和反馈
        score = state.get("score")
        feedback = state.get("feedback")
        
        # 如果有人工审核结果，使用人工审核结果
        if state.get("manual_review_score") is not None:
            score = state["manual_review_score"]
            feedback = state.get("manual_review_feedback", feedback)
            logger.info(f"使用人工审核结果，分数: {score}")
        
        # 检查是否已存在批改记录
        existing_correction = db.query(Correction).filter(
            Correction.homework_id == state["homework_id"]
        ).first()
        
        if existing_correction:
            # 更新现有记录
            existing_correction.ocr_text = state.get("ocr_text")
            existing_correction.ocr_confidence = state.get("ocr_confidence")
            existing_correction.ocr_details = state.get("ocr_details")
            existing_correction.score = score
            existing_correction.feedback = feedback
            existing_correction.errors = state.get("errors", [])
            existing_correction.status = "completed"
            existing_correction.needs_manual_review = 0
            logger.info(f"更新批改记录，作业ID: {state['homework_id']}")
        else:
            # 创建新记录
            correction = Correction(
                homework_id=state["homework_id"],
                ocr_text=state.get("ocr_text"),
                ocr_confidence=state.get("ocr_confidence"),
                ocr_details=state.get("ocr_details"),
                score=score,
                feedback=feedback,
                errors=state.get("errors", []),
                status="completed",
                needs_manual_review=0
            )
            db.add(correction)
            logger.info(f"创建新批改记录，作业ID: {state['homework_id']}")
        
        db.commit()
        
        # 更新作业状态
        homework = db.query(Homework).filter(Homework.id == state["homework_id"]).first()
        if homework:
            homework.status = "completed"
            db.commit()
            logger.info(f"更新作业状态为completed，作业ID: {state['homework_id']}")
        
        return {
            "status": "completed"
        }
        
    except Exception as e:
        logger.exception(f"保存结果失败: {str(e)}")
        db.rollback()
        return {
            "status": "save_failed"
        }
    finally:
        db.close()


def build_correction_graph() -> StateGraph:
    """
    构建批改流水线状态图
    
    流程：
    ocr_agent → scoring_agent → quality_agent → [条件路由]
                                        ├→ human_review（中断等待人工审核）→ save_result
                                        └→ save_result
    
    Returns:
        编译后的StateGraph
    """
    logger.info("开始构建批改流水线状态图")
    
    # 创建状态图构建器
    builder = StateGraph(CorrectionState)
    
    # 添加节点
    builder.add_node("ocr_agent", ocr_agent)
    builder.add_node("scoring_agent", scoring_agent)
    builder.add_node("quality_agent", quality_agent)
    builder.add_node("human_review", human_review_node)
    builder.add_node("save_result", save_result_node)
    
    # 设置入口点
    builder.set_entry_point("ocr_agent")
    
    # 添加边
    builder.add_edge("ocr_agent", "scoring_agent")
    builder.add_edge("scoring_agent", "quality_agent")
    
    # 添加条件边
    builder.add_conditional_edges(
        "quality_agent",
        route_after_quality,
        {
            "human_review": "human_review",
            "save_result": "save_result"
        }
    )
    
    # 人工审核后保存结果
    builder.add_edge("human_review", "save_result")
    
    # 保存结果后结束
    builder.add_edge("save_result", END)
    
    # 编译图，使用MemorySaver作为检查点
    # 在human_review节点前中断，等待人工审核
    graph = builder.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["human_review"]
    )
    
    logger.info("批改流水线状态图构建完成")
    return graph


# 编译后的图实例，供外部调用
compiled_graph = build_correction_graph()


def resume_with_human_review(
    homework_id: int,
    score: float,
    feedback: str,
    review_notes: str = ""
) -> Dict[str, Any]:
    """
    使用人工审核结果恢复流水线执行
    
    当教师完成人工审核后，调用此函数恢复LangGraph执行。
    使用标准的 update_state + invoke 模式恢复，而非 Command(resume)。
    
    Args:
        homework_id: 作业ID
        score: 人工审核分数
        feedback: 人工审核评语
        review_notes: 审核备注
        
    Returns:
        流水线执行结果
    """
    logger.info(f"恢复流水线执行，作业ID: {homework_id}, 分数: {score}")
    
    try:
        # 构建线程配置
        thread_config = {"configurable": {"thread_id": str(homework_id)}}
        
        # 第一步：更新状态，写入人工审核结果
        # 这会更新被中断的 human_review 节点的状态
        state_update = {
            "manual_review_score": score,
            "manual_review_feedback": feedback,
            "status": "human_reviewed"
        }
        compiled_graph.update_state(thread_config, state_update)
        logger.info(f"已更新状态: {state_update}")
        
        # 第二步：恢复执行
        # 传入 None 表示从上次中断的地方继续执行
        result = compiled_graph.invoke(None, config=thread_config)
        
        logger.info(f"流水线恢复执行完成，作业ID: {homework_id}, 结果: {result.get('status')}")
        return result
        
    except Exception as e:
        logger.exception(f"恢复流水线执行失败: {str(e)}")
        raise
