import cv2
import numpy as np
import pytesseract
from PIL import Image
from typing import Dict, Any, Tuple
from app.core.config import settings


class OCRService:
    """OCR识别服务"""
    
    def __init__(self):
        self.lang = settings.OCR_LANG
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """图像预处理"""
        # 读取图像
        image = cv2.imread(image_path)
        
        # 转为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 去噪
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # 二值化
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def recognize(self, image_path: str) -> Dict[str, Any]:
        """
        识别图像中的文字
        
        Returns:
            {
                "text": "识别的文本",
                "confidence": 平均置信度,
                "details": [详细识别结果]
            }
        """
        try:
            # 预处理图像
            processed_image = self.preprocess_image(image_path)
            
            # 使用Tesseract进行OCR识别
            data = pytesseract.image_to_data(
                processed_image,
                lang=self.lang,
                output_type=pytesseract.Output.DICT
            )
            
            # 提取文本和置信度
            texts = []
            confidences = []
            details = []
            
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 0:  # 过滤无效结果
                    text = data['text'][i].strip()
                    if text:
                        conf = int(data['conf'][i])
                        texts.append(text)
                        confidences.append(conf)
                        details.append({
                            "text": text,
                            "confidence": conf / 100.0,
                            "x": data['left'][i],
                            "y": data['top'][i],
                            "width": data['width'][i],
                            "height": data['height'][i]
                        })
            
            full_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0
            
            return {
                "text": full_text,
                "confidence": round(avg_confidence, 4),
                "details": details
            }
            
        except Exception as e:
            return {
                "text": "",
                "confidence": 0,
                "details": [],
                "error": str(e)
            }
    
    def needs_manual_review(self, confidence: float) -> bool:
        """判断是否需要人工审核"""
        return confidence < settings.MANUAL_REVIEW_THRESHOLD


ocr_service = OCRService()
