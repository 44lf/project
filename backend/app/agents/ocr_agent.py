"""
OCR识别Agent节点

负责调用OCR服务识别作业图片中的文字内容
"""

import logging
from typing import Dict, Any

from app.agents.state import CorrectionState
from app.services.ocr_service import ocr_service

logger = logging.getLogger(__name__)


def ocr_agent(state: CorrectionState) -> Dict[str, Any]:
    """
    OCR识别Agent节点
    
    调用OCR服务识别作业图片，提取文字内容和置信度信息
    
    Args:
        state: 当前流水线状态，包含image_path等字段
        
    Returns:
        包含ocr_text, ocr_confidence, ocr_details的字典
        
    Raises:
        无异常抛出，OCR失败时设置status="ocr_failed"并记录日志
    """
    logger.info(f"开始OCR识别，作业ID: {state['homework_id']}, 图片路径: {state['image_path']}")
    
    try:
        # 调用OCR服务识别图片
        ocr_result = ocr_service.recognize(state["image_path"])
        
        # 检查OCR是否成功
        if "error" in ocr_result:
            logger.error(f"OCR识别失败: {ocr_result['error']}")
            return {
                "ocr_text": "",
                "ocr_confidence": 0.0,
                "ocr_details": [],
                "status": "ocr_failed"
            }
        
        # 提取OCR结果
        ocr_text = ocr_result.get("text", "")
        ocr_confidence = ocr_result.get("confidence", 0.0)
        ocr_details = ocr_result.get("details", [])
        
        logger.info(f"OCR识别完成，置信度: {ocr_confidence:.4f}, 文本长度: {len(ocr_text)}")
        
        return {
            "ocr_text": ocr_text,
            "ocr_confidence": ocr_confidence,
            "ocr_details": ocr_details
        }
        
    except Exception as e:
        logger.exception(f"OCR识别异常: {str(e)}")
        return {
            "ocr_text": "",
            "ocr_confidence": 0.0,
            "ocr_details": [],
            "status": "ocr_failed"
        }
