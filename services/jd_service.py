"""JD 分析服务"""

import json
from typing import Dict, Any

from models import JDAnalysisResult
from services.llm_client import llm
from services.prompts import JDPrompts
from core.cache_manager import cached_analysis


def analyze_jd(job_description: str) -> JDAnalysisResult:
    """分析职位描述"""
    prompt = JDPrompts.jd_analysis_prompt()
    
    # 手动构建链，避免类型问题
    inputs = {"job_description": job_description}
    
    def call_llm():
        formatted_prompt = prompt.invoke(inputs)
        response = llm.invoke(formatted_prompt)
        
        # 解析 JSON 响应
        parser = PydanticOutputParser(pydantic_object=JDAnalysisResult)
        return parser.parse(response.content)
    
    return cached_analysis("analyze_jd", inputs, call_llm)


__all__ = ["analyze_jd"]