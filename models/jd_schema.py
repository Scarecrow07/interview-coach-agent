from pydantic import BaseModel, Field
from typing import Literal, Dict, Any


class ResponsibilityItem(BaseModel):
    """核心职责"""
    responsibility: str = Field(description="职责描述")
    business_goal: str = Field(description="对应业务目标")
    key_actions: list[str] = Field(description="关键动作，最多5条")
    priority: Literal["高", "中", "低"] = Field(description="优先级")


class HardRequirement(BaseModel):
    """硬性要求"""
    requirement: str = Field(description="要求描述")
    type: Literal["一票否决", "刚性偏好"] = Field(description="要求类型")
    evidence_in_jd: str = Field(description="JD中的证据")
    verify_method: str = Field(description="面试验证方法")


class SoftRequirement(BaseModel):
    """软性要求"""
    requirement: str = Field(description="软性要求描述")
    inference_basis: str = Field(description="推断依据")
    importance: Literal["高", "中", "低"] = Field(description="重要性")


class InterviewQuestion(BaseModel):
    """面试问题"""
    category: Literal["技术", "项目", "行为", "场景"] = Field(description="问题类别")
    question: str = Field(description="问题内容")
    difficulty: Literal["初级", "中级", "高级"] = Field(description="难度等级")
    intent: str = Field(description="考察意图")
    evaluation_criteria: list[str] = Field(description="评分标准，最多3条")


class JDAnalysisResult(BaseModel):
    """JD分析结果"""
    job_profile: Dict[str, str] = Field(description="岗位画像")
    core_responsibilities: list[ResponsibilityItem] = Field(description="核心职责，最多5条")
    hard_requirements: list[HardRequirement] = Field(description="硬性要求")
    soft_requirements: list[SoftRequirement] = Field(description="软性要求")
    hidden_insights: Dict[str, Any] = Field(description="隐藏信息挖掘")
    interview_questions: list[InterviewQuestion] = Field(description="高频问题，固定5条")