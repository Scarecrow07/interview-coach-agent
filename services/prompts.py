"""Prompt templates for all analysis steps"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from models import (
    ResumeDocument, JDAnalysisResult, ResumeAnalysisResult,
    MatchAnalysisResult, QABank
)


class ResumePrompts:
    """简历相关 Prompt 模板"""
    
    @staticmethod
    def create_resume_prompt() -> ChatPromptTemplate:
        """创建简历 Prompt"""
        parser = PydanticOutputParser(pydantic_object=ResumeDocument)
        
        template = """你是专业的简历撰写顾问。请根据用户提供的背景描述，生成结构化的简历草稿。

用户背景信息：
{user_background}

{format_instructions}

关键要求：

1. 结构完整性：必须包含个人信息、个人总结、工作经历、项目经历、教育背景、技能。信息不足的字段标注在missing_fields中。

2. STAR-L原则：工作经历中的star_achievements使用STAR-L结构。每条成就必须包含量化数字。

3. 量化成果：achievements和results必须包含具体数字。

4. 技能分组：按category分组，每组标注proficiency。

5. 信息不足处理：用户未提供的信息标注在missing_fields中，不要虚构任何信息。

6. 输出格式：填充所有字段，生成raw_text：Markdown格式的完整简历文本。

请严格按照Schema输出。"""
        
        return ChatPromptTemplate.from_template(template).partial(
            format_instructions=parser.get_format_instructions()
        )
    
    @staticmethod
    def parse_resume_prompt() -> ChatPromptTemplate:
        """解析简历 Prompt"""
        parser = PydanticOutputParser(pydantic_object=ResumeDocument)
        
        template = """你是简历解析专家。请将以下简历文本解析为结构化格式。

简历文本：
{resume_text}

{format_instructions}

解析要求：

1. 准确提取所有可见信息
2. 工作经历按时间倒序排列
3. 技能分组并标注熟练程度
4. 不虚构任何信息
5. 同时生成raw_text：Markdown格式的完整简历

请严格按照Schema输出。"""
        
        return ChatPromptTemplate.from_template(template).partial(
            format_instructions=parser.get_format_instructions()
        )
    
    @staticmethod
    def optimize_resume_prompt() -> ChatPromptTemplate:
        """优化简历 Prompt"""
        from models.resume_schema import OptimizedResume
        
        parser = PydanticOutputParser(pydantic_object=OptimizedResume)
        
        template = """你是资深简历优化专家。请优化简历并提供详细说明。

当前简历（JSON格式）：
{current_resume}

目标职位描述（若为空则进行通用优化）：
{job_description}

{format_instructions}

优化原则：

1. 结构调整：调整顺序使最相关的工作/项目在前，控制在1-2页打印篇幅。
2. 内容强化：每条经历包含量化成果，使用STAR-L结构。
3. 关键词植入：从JD中提取关键词自然植入。
4. 量化改进：所有模糊描述改为具体数字。
5. 真实性校验：不虚构任何信息。

请严格按照Schema输出。"""
        
        return ChatPromptTemplate.from_template(template).partial(
            format_instructions=parser.get_format_instructions()
        )


class JDPrompts:
    """JD 分析 Prompt 模板"""
    
    @staticmethod
    def jd_analysis_prompt() -> ChatPromptTemplate:
        """JD 分析 Prompt"""
        parser = PydanticOutputParser(pydantic_object=JDAnalysisResult)
        
        template = """你是资深招聘专家。请分析以下职位描述。

职位描述：
{job_description}

{format_instructions}

关键要求：

1. 核心职责提炼：转化为业务目标+关键动作，标注优先级。
2. 硬性要求清单：标注"一票否决"或"刚性偏好"，提供JD证据和面试验证方法。
3. 软性要求推断：注明推断依据和重要性。
4. 隐藏信息挖掘：挖掘阶段暗示、急需解决的问题。
5. 面试高频问题：固定输出5条，覆盖技术、项目、行为、场景四类。

请严格按照Schema输出。"""
        
        return ChatPromptTemplate.from_template(template).partial(
            format_instructions=parser.get_format_instructions()
        )


class ResumeAnalysisPrompts:
    """简历分析 Prompt 模板"""
    
    @staticmethod
    def resume_analysis_prompt() -> ChatPromptTemplate:
        """简历分析 Prompt"""
        parser = PydanticOutputParser(pydantic_object=ResumeAnalysisResult)
        
        template = """你是资深职业规划师与面试教练。请对以下简历进行深度分析。

简历内容：
{resume_text}

JD 分析报告（若为空则进行通用分析）：
{jd_report}

{format_instructions}

关键要求：

1. 成就事件使用STAR-L结构，优先选择与JD匹配的经历。
2. 风险识别需标注严重程度并提供应对策略。
3. 若提供了JD报告，需强调关联点。
4. 所有字段必须符合Schema定义。

请严格按照Schema输出。"""
        
        return ChatPromptTemplate.from_template(template).partial(
            format_instructions=parser.get_format_instructions()
        )


class MatchPrompts:
    """匹配度分析 Prompt 模板"""
    
    @staticmethod
    def match_analysis_prompt() -> ChatPromptTemplate:
        """匹配度分析 Prompt"""
        parser = PydanticOutputParser(pydantic_object=MatchAnalysisResult)
        
        template = """你是资深招聘匹配专家。请分析候选人与岗位的匹配度。

JD 分析报告：
{jd_report}

简历分析报告：
{resume_report}

{format_instructions}

关键要求：

1. 能力匹配明细表：逐一对比JD要求与候选人能力。
2. 差距弥补方案：区分短期可弥补和短期难弥补。
3. 核心优势强化：提炼2-3个核心优势。
4. 风险应对锦囊：针对简历风险提供面试应对策略。
5. 面试准备策略总纲：综合建议。

请严格按照Schema输出。"""
        
        return ChatPromptTemplate.from_template(template).partial(
            format_instructions=parser.get_format_instructions()
        )


class InterviewPrompts:
    """面试方案 Prompt 模板"""
    
    @staticmethod
    def self_intro_prompt() -> ChatPromptTemplate:
        """自我介绍 Prompt"""
        template = """你是面试辅导专家。请为候选人定制自我介绍。

简历分析：
{resume_report}

JD分析：
{jd_report}

匹配度报告：
{match_report}

请生成一份精炼的自我介绍，包含以下要素：

1. 核心身份定位（一句话）
2. 核心经历亮点（2-3个，每个用STAR结构）
3. 与岗位的契合点
4. 个人价值主张

输出格式：
{
  "brief_intro": "一句话介绍（30秒版本）",
  "standard_intro": "标准自我介绍（1-2分钟版本，约300字）",
  "key_points": ["要点列表"],
  "personalization": "如何根据面试现场调整"
}

请直接输出JSON格式结果。"""
        
        return ChatPromptTemplate.from_template(template)
    
    @staticmethod
    def project_intro_prompt() -> ChatPromptTemplate:
        """项目介绍 Prompt"""
        template = """你是面试辅导专家。请为候选人定制项目介绍方案。

简历分析：
{resume_report}

JD分析：
{jd_report}

匹配度报告：
{match_report}

请选择简历中最值得介绍的2-3个项目，为每个项目生成介绍方案：

输出格式：
[
  {
    "project_name": "项目名称",
    "selection_reason": "选择该项目的原因",
    "brief_intro": "一句话介绍（30秒版本）",
    "detailed_intro": "详细介绍（2-3分钟，包含背景、挑战、行动、结果）",
    "tech_highlights": ["技术亮点"],
    "面试官可能的追问": ["可能的追问列表"],
    "回答策略": "追问回答策略"
  }
]

请直接输出JSON格式结果。"""
        
        return ChatPromptTemplate.from_template(template)
    
    @staticmethod
    def qa_bank_prompt() -> ChatPromptTemplate:
        """问答库 Prompt"""
        parser = PydanticOutputParser(pydantic_object=QABank)
        
        template = """你是面试题库设计专家。请生成定制化问答库。

JD分析：
{jd_report}

简历分析：
{resume_report}

匹配度报告：
{match_report}

{format_instructions}

关键要求：

1. 总数固定为15条，每类2-3条。
2. 优先输出JD分析中预测的高频问题，标记为"高频必答"。
3. sample_answer必须为可直接口述的完整回答（200-300字）。
4. personalization需说明如何植入候选人优势。

请严格按照Schema输出。"""
        
        return ChatPromptTemplate.from_template(template).partial(
            format_instructions=parser.get_format_instructions()
        )
    
    @staticmethod
    def written_test_prompt() -> ChatPromptTemplate:
        """笔试题目 Prompt"""
        template = """你是技术面试题设计专家。请生成笔试题目。

JD分析：
{jd_report}

匹配度报告：
{match_report}

请生成5道笔试题目，覆盖JD中的核心技术要求：

输出格式：
{
  "questions": [
    {
      "id": "T001",
      "category": "算法/数据结构/系统设计/编程/场景",
      "title": "题目名称",
      "description": "题目描述",
      "difficulty": "初级/中级/高级",
      "time_estimate": "预计用时",
      "hints": ["提示"],
      "reference_solution": "参考解法思路",
      "evaluation_criteria": ["评分标准"]
    }
  ],
  "total_count": 5,
  "time_limit_recommendation": "建议总用时"
}

请直接输出JSON格式结果。"""
        
        return ChatPromptTemplate.from_template(template)


# 导出所有 Prompt 类
__all__ = [
    "ResumePrompts", "JDPrompts", "ResumeAnalysisPrompts",
    "MatchPrompts", "InterviewPrompts"
]