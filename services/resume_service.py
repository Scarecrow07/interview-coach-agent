"""简历服务"""

import json
from typing import Dict, Any, Optional

from langchain_core.output_parsers import PydanticOutputParser

from models import ResumeDocument
from models.resume_schema import OptimizedResume
from services.llm_client import llm
from services.prompts import ResumePrompts
from core.cache_manager import cached_analysis


def create_resume_from_background(user_background: str) -> ResumeDocument:
    """根据用户背景创建简历"""
    parser = PydanticOutputParser(pydantic_object=ResumeDocument)
    prompt = ResumePrompts.create_resume_prompt()
    chain = prompt | llm | parser
    
    inputs = {"user_background": user_background}
    
    return cached_analysis(
        "create_resume",
        inputs,
        lambda: chain.invoke(inputs)
    )


def parse_resume_to_structured(resume_text: str) -> ResumeDocument:
    """解析上传的简历为结构化格式"""
    parser = PydanticOutputParser(pydantic_object=ResumeDocument)
    prompt = ResumePrompts.parse_resume_prompt()
    chain = prompt | llm | parser
    
    inputs = {"resume_text": resume_text}
    
    return cached_analysis(
        "parse_resume",
        inputs,
        lambda: chain.invoke(inputs)
    )


def optimize_resume(
    current_resume: ResumeDocument,
    job_description: Optional[str] = None,
    jd_report: Optional[Dict[str, Any]] = None
) -> OptimizedResume:
    """优化简历"""
    parser = PydanticOutputParser(pydantic_object=OptimizedResume)
    prompt = ResumePrompts.optimize_resume_prompt()
    chain = prompt | llm | parser
    
    inputs = {
        "current_resume": current_resume.model_dump_json(),
        "job_description": job_description or "",
        "jd_report": json.dumps(jd_report) if jd_report else "",
    }
    
    return cached_analysis(
        "optimize_resume",
        inputs,
        lambda: chain.invoke(inputs)
    )


__all__ = ["create_resume_from_background", "parse_resume_to_structured", "optimize_resume"]