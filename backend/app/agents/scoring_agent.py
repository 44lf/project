"""
LLM智能评分Agent节点

负责调用大语言模型对OCR识别结果进行智能评分
"""

import json
import logging
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field

from app.agents.state import CorrectionState, ErrorDetail
from app.core.config import settings

logger = logging.getLogger(__name__)


class ScoringResult(BaseModel):
    """评分结果模型"""
    score: float = Field(description="得分，范围0-100")
    feedback: str = Field(description="评语")
    errors: List[Dict[str, str]] = Field(description="错误列表，每项包含type和description")


# 创建输出解析器
output_parser = PydanticOutputParser(pydantic_object=ScoringResult)


def _load_scoring_prompt_template() -> str:
    """加载评分提示词模板"""
    import os
    template_path = os.path.join(
        os.path.dirname(__file__), 
        "prompts", 
        "scoring_prompt.j2"
    )
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"模板文件不存在: {template_path}，使用默认模板")
        # 默认模板
        return """你是一位K12教育领域的专业教师，正在批改学生的{{subject}}作业。

作业信息

学科：{{subject}}
OCR识别内容：
{{ocr_text}}

评分要求
请根据以下标准评分（满分100分）：

内容完整性（40分）：作业内容是否完整
正确性（40分）：答案是否正确
书写规范（20分）：书写是否工整规范

请严格按以下JSON格式输出，不要输出其他内容：
{"score": <float>, "feedback": "<评语>", "errors": [{"type": "<错误类型>", "description": "<错误描述>"}]}
"""


def scoring_agent(state: CorrectionState) -> Dict[str, Any]:
    """
    LLM智能评分Agent节点
    
    使用大语言模型根据OCR识别结果进行智能评分
    
    Args:
        state: 当前流水线状态，包含ocr_text, subject等字段
        
    Returns:
        包含score, feedback, errors的字典
        
    Raises:
        无异常抛出，评分失败时设置status="scoring_failed"并记录日志
    """
    logger.info(f"开始智能评分，作业ID: {state['homework_id']}, 学科: {state['subject']}")
    
    try:
        # 检查OCR结果是否有效
        if not state.get("ocr_text") or state.get("status") == "ocr_failed":
            logger.warning("OCR结果无效，无法进行评分")
            return {
                "score": None,
                "feedback": "OCR识别失败，无法评分",
                "errors": [{"type": "ocr_failed", "description": "文字识别失败"}],
                "status": "scoring_failed"
            }
        
        # 初始化LLM
        llm = ChatOpenAI(
            model=settings.LLM_MODEL_NAME,
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
            temperature=0.3,
            max_tokens=2000
        )
        
        # 加载并渲染提示词模板
        prompt_template = _load_scoring_prompt_template()
        
        # 使用Jinja2风格渲染模板
        from jinja2 import Template
        template = Template(prompt_template)
        prompt_text = template.render(
            subject=state["subject"],
            ocr_text=state["ocr_text"]
        )
        
        # 调用LLM
        logger.debug(f"发送评分请求，Prompt长度: {len(prompt_text)}")
        response = llm.invoke(prompt_text)
        response_content = response.content
        
        logger.debug(f"收到LLM响应: {response_content[:200]}...")
        
        # 解析JSON响应
        try:
            # 尝试直接解析
            result = json.loads(response_content)
        except json.JSONDecodeError:
            # 尝试从文本中提取JSON
            import re
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError("无法解析LLM响应为JSON")
        
        # 验证结果
        score = float(result.get("score", 0))
        feedback = result.get("feedback", "")
        errors_raw = result.get("errors", [])
        
        # 格式化错误列表
        errors: List[ErrorDetail] = []
        for error in errors_raw:
            errors.append({
                "type": error.get("type", "unknown"),
                "description": error.get("description", "")
            })
        
        # 确保分数在有效范围内
        score = max(0, min(100, score))
        
        logger.info(f"智能评分完成，得分: {score}")
        
        return {
            "score": score,
            "feedback": feedback,
            "errors": errors
        }
        
    except Exception as e:
        logger.exception(f"智能评分异常: {str(e)}")
        return {
            "score": None,
            "feedback": f"评分失败: {str(e)}",
            "errors": [{"type": "scoring_error", "description": str(e)}],
            "status": "scoring_failed"
        }
