"""OCR识别Agent节点"""
import logging
from typing import Dict, Any
from app.agents.state import CorrectionState
from app.services.ocr_service import ocr_service

logger = logging.getLogger(__name__)


def ocr_agent(state: CorrectionState) -> Dict[str, Any]:
    """OCR识别Agent，调用OCR服务识别作业图片"""
    logger.info(f"开始OCR识别，作业ID: {state['homework_id']}")
    
    try:
        ocr_result = ocr_service.recognize(
            state["image_path"],
            state.get("subject", "chinese")
        )
        
        if "error" in ocr_result:
            logger.error(f"OCR识别失败: {ocr_result['error']}")
            return {
                "ocr_text": "",
                "ocr_confidence": 0.0,
                "ocr_details": [],
                "status": "ocr_failed"
            }
        
        ocr_text = ocr_result.get("text", "")
        ocr_confidence = ocr_result.get("confidence", 0.0)
        ocr_details = ocr_result.get("details", [])
        
        logger.info(f"OCR完成，置信度: {ocr_confidence:.4f}")
        return {
            "ocr_text": ocr_text,
            "ocr_confidence": ocr_confidence,
            "ocr_details": ocr_details
        }
        
    except Exception as e:
        logger.exception(f"OCR异常: {str(e)}")
        return {
            "ocr_text": "",
            "ocr_confidence": 0.0,
            "ocr_details": [],
            "status": "ocr_failed"
        }
