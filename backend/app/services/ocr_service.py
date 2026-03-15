"""
OCR识别服务

支持两种模式：
1. PaddleOCR模式 - 使用paddleocr库进行真实OCR识别
2. Mock模式 - 模拟OCR结果，用于demo演示和无GPU环境

通过config.OCR_ENGINE切换模式
"""

import cv2
import numpy as np
import random
import logging
from typing import Dict, Any, List
from abc import ABC, abstractmethod

from app.core.config import settings
from app.services.ocr_mock_data import get_mock_text

logger = logging.getLogger(__name__)


class BaseOCREngine(ABC):
    """OCR引擎基类"""
    
    @abstractmethod
    def recognize(self, image_path: str, subject: str = None) -> Dict[str, Any]:
        """
        识别图像中的文字
        
        Args:
            image_path: 图像文件路径
            subject: 学科类型（用于mock模式）
            
        Returns:
            包含text、confidence、details的字典
        """
        pass
    
    def needs_manual_review(self, confidence: float) -> bool:
        """
        判断是否需要人工审核
        
        Args:
            confidence: OCR置信度
            
        Returns:
            是否需要人工审核
        """
        return confidence < settings.MANUAL_REVIEW_THRESHOLD


class PaddleOCREngine(BaseOCREngine):
    """PaddleOCR引擎"""
    
    def __init__(self):
        """初始化PaddleOCR"""
        self.ocr = None
        self._init_ocr()
    
    def _init_ocr(self):
        """延迟初始化OCR引擎"""
        if self.ocr is None:
            try:
                from paddleocr import PaddleOCR
                self.ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang='ch',
                    use_gpu=settings.PADDLEOCR_USE_GPU,
                    show_log=False
                )
                logger.info("PaddleOCR初始化成功")
            except ImportError:
                logger.error("paddleocr未安装，请执行: pip install paddleocr")
                raise
            except Exception as e:
                logger.exception(f"PaddleOCR初始化失败: {str(e)}")
                raise
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        图像预处理
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            预处理后的图像数组
        """
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")
            
            # 转为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 去噪
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # 二值化
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return binary
            
        except Exception as e:
            logger.exception(f"图像预处理失败: {str(e)}")
            # 返回原图
            return cv2.imread(image_path)
    
    def recognize(self, image_path: str, subject: str = None) -> Dict[str, Any]:
        """
        使用PaddleOCR识别图像中的文字
        
        Args:
            image_path: 图像文件路径
            subject: 学科类型（PaddleOCR模式下不使用）
            
        Returns:
            {
                "text": "识别的文本",
                "confidence": 平均置信度,
                "details": [详细识别结果]
            }
        """
        logger.info(f"使用PaddleOCR识别图像: {image_path}")
        
        try:
            # 执行OCR识别
            result = self.ocr.ocr(image_path, cls=True)
            
            if result is None or len(result) == 0:
                logger.warning(f"OCR未识别到文字: {image_path}")
                return {
                    "text": "",
                    "confidence": 0.0,
                    "details": []
                }
            
            # 解析结果
            texts = []
            confidences = []
            details = []
            
            # result是列表的列表，每个元素包含文本框坐标和识别结果
            for line in result:
                if line is None:
                    continue
                for item in line:
                    if item is None:
                        continue
                    # item格式: [文本框坐标, (识别文本, 置信度)]
                    box = item[0]
                    text_info = item[1]
                    
                    if isinstance(text_info, tuple) and len(text_info) >= 2:
                        text = text_info[0]
                        conf = text_info[1]
                        
                        texts.append(text)
                        confidences.append(conf)
                        
                        # 计算文本框中心点
                        box_array = np.array(box)
                        center_x = int(np.mean(box_array[:, 0]))
                        center_y = int(np.mean(box_array[:, 1]))
                        width = int(np.max(box_array[:, 0]) - np.min(box_array[:, 0]))
                        height = int(np.max(box_array[:, 1]) - np.min(box_array[:, 1]))
                        
                        details.append({
                            "text": text,
                            "confidence": round(conf, 4),
                            "x": center_x - width // 2,
                            "y": center_y - height // 2,
                            "width": width,
                            "height": height,
                            "box": box
                        })
            
            full_text = '\n'.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            logger.info(f"PaddleOCR识别完成，置信度: {avg_confidence:.4f}, 文本长度: {len(full_text)}")
            
            return {
                "text": full_text,
                "confidence": round(avg_confidence, 4),
                "details": details
            }
            
        except Exception as e:
            logger.exception(f"PaddleOCR识别失败: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "details": [],
                "error": str(e)
            }


class MockOCREngine(BaseOCREngine):
    """Mock OCR引擎（模拟模式）"""
    
    def __init__(self):
        """初始化Mock引擎"""
        logger.info("Mock OCR引擎初始化成功（用于demo演示）")
    
    def recognize(self, image_path: str, subject: str = "chinese") -> Dict[str, Any]:
        """
        模拟OCR识别结果
        
        Args:
            image_path: 图像文件路径（仅用于生成确定性随机种子）
            subject: 学科类型，决定返回哪种模拟文本
            
        Returns:
            {
                "text": "模拟的OCR文本",
                "confidence": 随机置信度(0.5~0.95),
                "details": [模拟的详细结果]
            }
        """
        logger.info(f"使用Mock OCR模拟识别，学科: {subject}")
        
        try:
            # 使用图像路径生成确定性随机种子（相同图片返回相同结果）
            seed = hash(image_path) % 10000
            random.seed(seed)
            
            # 生成随机置信度（0.5~0.95之间）
            confidence = round(random.uniform(0.50, 0.95), 4)
            
            # 获取模拟文本
            mock_text = get_mock_text(subject)
            
            # 生成模拟的details
            lines = mock_text.split('\n')
            details = []
            y_position = 50
            
            for i, line in enumerate(lines):
                if line.strip():
                    line_confidence = round(random.uniform(0.60, 0.95), 4)
                    details.append({
                        "text": line,
                        "confidence": line_confidence,
                        "x": random.randint(20, 100),
                        "y": y_position,
                        "width": len(line) * 15 + random.randint(0, 50),
                        "height": random.randint(20, 35),
                        "box": None  # Mock模式没有真实文本框
                    })
                    y_position += random.randint(30, 50)
            
            logger.info(f"Mock OCR生成完成，置信度: {confidence:.4f}")
            
            return {
                "text": mock_text,
                "confidence": confidence,
                "details": details
            }
            
        except Exception as e:
            logger.exception(f"Mock OCR生成失败: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "details": [],
                "error": str(e)
            }
        finally:
            # 重置随机种子
            random.seed()
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Mock模式下的图像预处理（返回空数组）
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            空numpy数组
        """
        logger.debug("Mock模式跳过图像预处理")
        return np.array([])


class OCRService:
    """OCR服务统一入口"""
    
    def __init__(self):
        """初始化OCR服务"""
        self._engine: BaseOCREngine = None
        self._engine_type: str = None
        self._init_engine()
    
    def _init_engine(self):
        """根据配置初始化OCR引擎"""
        engine_type = settings.OCR_ENGINE.lower()
        
        if engine_type == "paddleocr":
            try:
                self._engine = PaddleOCREngine()
                self._engine_type = "paddleocr"
                logger.info("OCR服务使用PaddleOCR引擎")
            except Exception as e:
                logger.error(f"PaddleOCR引擎初始化失败，回退到Mock模式: {str(e)}")
                self._engine = MockOCREngine()
                self._engine_type = "mock"
        else:
            self._engine = MockOCREngine()
            self._engine_type = "mock"
            logger.info("OCR服务使用Mock引擎（用于demo演示）")
    
    def recognize(self, image_path: str, subject: str = "chinese") -> Dict[str, Any]:
        """
        识别图像中的文字
        
        Args:
            image_path: 图像文件路径
            subject: 学科类型（用于mock模式选择对应文本）
            
        Returns:
            包含text、confidence、details的字典
        """
        return self._engine.recognize(image_path, subject)
    
    def needs_manual_review(self, confidence: float) -> bool:
        """
        判断是否需要人工审核
        
        Args:
            confidence: OCR置信度
            
        Returns:
            是否需要人工审核
        """
        return self._engine.needs_manual_review(confidence)
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        图像预处理
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            预处理后的图像数组（Mock模式返回空数组）
        """
        if hasattr(self._engine, 'preprocess_image'):
            return self._engine.preprocess_image(image_path)
        return np.array([])
    
    @property
    def engine_type(self) -> str:
        """获取当前使用的引擎类型"""
        return self._engine_type


# 全局OCR服务实例
ocr_service = OCRService()
