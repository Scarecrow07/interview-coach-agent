"""简历分析服务"""

import json
from typing import Dict, Any, Optional

from langchain_core.output_parsers import PydanticOutputParser

from models import ResumeAnalysisResult, ResumeDocument, JDAnalysisResult
from services.llm_client import llm
from services.prompts import ResumeAnalysisPrompts
from core.cache_manager import cached_analysis


def analyze_resume(
    resume: ResumeDocument,
    jd_report: Optional[JDAnalysisResult] = None
) -> ResumeAnalysisResult:
    """分析简历"""
    parser = PydanticOutputParser(pydantic_object=ResumeAnalysisResult)
    prompt = ResumeAnalysisPrompts.resume_analysis_prompt()
    chain = prompt | llm | parser
    
    inputs = {
        "resume_text": resume.model_dump_json(),
        "jd_report": jd_report.model_dump_json() if jd_report else "",
    }
    
    return cached_analysis(
        "analyze_resume",
        inputs,
        lambda: chain.invoke(inputs)
    )


__all__ = ["analyze_resume"]