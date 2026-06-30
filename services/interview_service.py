"""面试方案生成服务"""

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any

from langchain_core.output_parsers import PydanticOutputParser

from models import QABank, ResumeAnalysisResult, JDAnalysisResult, MatchAnalysisResult
from services.llm_client import llm
from services.prompts import InterviewPrompts
from core.cache_manager import cached_analysis


class InterviewEngine:
    """面试方案生成引擎"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def generate_interview_plan_parallel(
        self,
        resume_report: ResumeAnalysisResult,
        jd_report: JDAnalysisResult,
        match_report: MatchAnalysisResult
    ) -> Dict[str, Any]:
        """并行生成面试方案三部分"""
        loop = asyncio.get_event_loop()
        
        intro_future = loop.run_in_executor(
            self.executor,
            lambda: self._generate_intro(resume_report, jd_report, match_report)
        )
        projects_future = loop.run_in_executor(
            self.executor,
            lambda: self._generate_projects(resume_report, jd_report, match_report)
        )
        qa_future = loop.run_in_executor(
            self.executor,
            lambda: self._generate_qa(resume_report, jd_report, match_report)
        )
        
        intro, projects, qa = await asyncio.gather(
            intro_future, projects_future, qa_future
        )
        
        return {
            "self_introduction": intro,
            "project_introductions": projects,
            "qa_bank": qa,
        }
    
    def _generate_intro(
        self,
        resume_report: ResumeAnalysisResult,
        jd_report: JDAnalysisResult,
        match_report: MatchAnalysisResult
    ) -> Dict[str, Any]:
        """生成自我介绍"""
        prompt = InterviewPrompts.self_intro_prompt()
        
        inputs = {
            "resume_report": resume_report.model_dump_json(),
            "jd_report": jd_report.model_dump_json(),
            "match_report": match_report.model_dump_json(),
        }
        
        result = cached_analysis(
            "generate_intro",
            inputs,
            lambda: self._call_and_parse_json(prompt, inputs)
        )
        
        return result
    
    def _generate_projects(
        self,
        resume_report: ResumeAnalysisResult,
        jd_report: JDAnalysisResult,
        match_report: MatchAnalysisResult
    ) -> list:
        """生成项目介绍"""
        prompt = InterviewPrompts.project_intro_prompt()
        
        inputs = {
            "resume_report": resume_report.model_dump_json(),
            "jd_report": jd_report.model_dump_json(),
            "match_report": match_report.model_dump_json(),
        }
        
        result = cached_analysis(
            "generate_projects",
            inputs,
            lambda: self._call_and_parse_json(prompt, inputs)
        )
        
        return result
    
    def _generate_qa(
        self,
        resume_report: ResumeAnalysisResult,
        jd_report: JDAnalysisResult,
        match_report: MatchAnalysisResult
    ) -> QABank:
        """生成问答库"""
        parser = PydanticOutputParser(pydantic_object=QABank)
        prompt = InterviewPrompts.qa_bank_prompt()
        chain = prompt | llm | parser
        
        inputs = {
            "jd_report": jd_report.model_dump_json(),
            "resume_report": resume_report.model_dump_json(),
            "match_report": match_report.model_dump_json(),
        }
        
        return cached_analysis(
            "generate_qa",
            inputs,
            lambda: chain.invoke(inputs)
        )
    
    def _call_and_parse_json(self, prompt, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """调用LLM并解析JSON响应"""
        formatted_prompt = prompt.invoke(inputs)
        response = llm.invoke(formatted_prompt)
        
        # 尝试解析JSON
        content = response.content
        
        # 提取JSON部分（可能被包裹在```json```中）
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "raw_content": content}


def generate_written_test(
    jd_report: JDAnalysisResult,
    match_report: MatchAnalysisResult
) -> Dict[str, Any]:
    """生成笔试题目"""
    prompt = InterviewPrompts.written_test_prompt()
    
    inputs = {
        "jd_report": jd_report.model_dump_json(),
        "match_report": match_report.model_dump_json(),
    }
    
    def call_and_parse():
        formatted_prompt = prompt.invoke(inputs)
        response = llm.invoke(formatted_prompt)
        
        content = response.content
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "raw_content": content}
    
    return cached_analysis("generate_written_test", inputs, call_and_parse)


# 全局引擎实例
interview_engine = InterviewEngine()


__all__ = ["InterviewEngine", "interview_engine", "generate_written_test"]