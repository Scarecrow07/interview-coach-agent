from pydantic import BaseModel, Field
from typing import Literal, Dict


class QAPair(BaseModel):
    """问答对"""
    id: str = Field(description="问题ID，格式Q001")
    category: Literal["专业技术", "项目深挖", "系统设计", "行为软技能", "动机规划", "短板风险"] = Field(description="问题类别")
    question: str = Field(description="问题内容")
    priority: Literal["高频必答", "常规题", "补充题"] = Field(description="优先级")
    intent: str = Field(description="考察意图")
    answer_framework: Dict[str, str] = Field(description="STAR-L框架要点")
    sample_answer: str = Field(description="完整回答示例，200-300字")
    key_points: list[str] = Field(description="高分要点，最多3条")
    pitfalls: list[str] = Field(description="需避开的雷区，最多3条")
    personalization: str = Field(description="植入候选人优势的方法")


class QABank(BaseModel):
    """问答库"""
    questions: list[QAPair] = Field(description="问答列表，固定15条")
    categories_count: Dict[str, int] = Field(description="各类别题目数量")