from pydantic import BaseModel, Field
from typing import Literal


class MatchItem(BaseModel):
    """能力匹配明细"""
    capability: str = Field(description="能力项")
    required_level: str = Field(description="要求程度")
    candidate_level: str = Field(description="候选人水平")
    match_status: Literal["强匹配", "弱匹配", "不匹配"] = Field(description="匹配状态")
    strategy: str = Field(description="面试体现策略")


class GapAnalysis(BaseModel):
    """差距弥补方案"""
    gap: str = Field(description="差距项")
    type: Literal["短期可弥补", "短期难弥补"] = Field(description="弥补类型")
    solution: str = Field(description="弥补方案")


class MatchAnalysisResult(BaseModel):
    """匹配度分析结果"""
    overall_score: Dict[str, str] = Field(description="整体匹配度评分")
    capability_match: list[MatchItem] = Field(description="能力匹配明细表")
    gap_analysis: list[GapAnalysis] = Field(description="差距弥补方案")
    core_advantages: list[str] = Field(description="核心优势强化，2-3个")
    risk_responses: list[str] = Field(description="风险应对锦囊")
    preparation_strategy: str = Field(description="面试准备策略总纲")