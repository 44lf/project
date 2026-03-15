"""
LangGraph多Agent批改系统

提供基于LangGraph的作业批改流水线，包含OCR识别、智能评分、质量检查等Agent节点。
"""

from app.agents.graph import compiled_graph
from app.agents.state import CorrectionState

__all__ = ["compiled_graph", "CorrectionState"]
