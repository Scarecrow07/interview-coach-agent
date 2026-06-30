"""匹配度分析服务"""

import json
from typing import Dict, Any

from langchain_core.output_parsers import PydanticOutputParser

from models import MatchAnalysisResult, ResumeAnalysisResult, JDAnalysisResult
from services.llm_client import llm
from services.prompts import MatchPrompts
from core.cache_manager import cached_analysis


def analyze_match(
    jd_report: JDAnalysisResult,
    resume_report: ResumeAnalysisResult
) -> MatchAnalysisResult:
    """分析匹配度"""
    parser = PydanticOutputParser(pydantic_object=MatchAnalysisResult)
    prompt = MatchPrompts.match_analysis_prompt()
    chain = prompt | llm | parser
    
    inputs = {
        "jd_report": jd_report.model_dump_json(),
        "resume_report": resume_report.model_dump_json(),
    }
    
    return cached_analysis(
        "analyze_match",
        inputs,
        lambda: chain.invoke(inputs)
    )


__all__ = ["analyze_match"]