from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any


class PersonalInfo(BaseModel):
    """个人信息"""
    name: str = Field(description="姓名")
    phone: Optional[str] = Field(description="手机号")
    email: Optional[str] = Field(description="邮箱")
    location: Optional[str] = Field(description="所在地")
    linkedin: Optional[str] = Field(description="LinkedIn链接")
    github: Optional[str] = Field(description="GitHub链接")


class PersonalSummary(BaseModel):
    """个人总结"""
    core_identity: str = Field(description="核心身份定位")
    years_experience: int = Field(description="工作年限")
    key_domains: list[str] = Field(description="核心领域，最多3个")
    value_proposition: str = Field(description="价值主张")
    highlights: list[str] = Field(description="亮点关键词，最多5个")


class STARAchievement(BaseModel):
    """STAR-L结构成就"""
    situation: str = Field(description="背景情境")
    task: str = Field(description="任务目标")
    action: list[str] = Field(description="关键行动，最多5条")
    result: str = Field(description="量化结果")
    learning: str = Field(description="复盘沉淀")


class WorkExperience(BaseModel):
    """工作经历"""
    company: str = Field(description="公司名称")
    position: str = Field(description="职位")
    start_date: str = Field(description="开始时间")
    end_date: Optional[str] = Field(description="结束时间")
    responsibilities: list[str] = Field(description="主要职责，最多5条")
    achievements: list[str] = Field(description="量化成就")
    technologies: list[str] = Field(description="使用的技术")
    star_achievements: list[STARAchievement] = Field(description="STAR-L成就，最多3条")


class ProjectExperience(BaseModel):
    """项目经历"""
    project_name: str = Field(description="项目名称")
    role: str = Field(description="角色")
    background: str = Field(description="背景与目标")
    key_challenges: list[str] = Field(description="关键挑战，最多3条")
    actions: list[str] = Field(description="关键行动，最多5条")
    results: str = Field(description="量化结果")
    learnings: Optional[str] = Field(description="复盘沉淀")
    technologies: list[str] = Field(description="技术栈")


class Education(BaseModel):
    """教育背景"""
    school: str = Field(description="学校名称")
    degree: str = Field(description="学位")
    major: str = Field(description="专业")
    start_date: str = Field(description="开始时间")
    end_date: str = Field(description="结束时间")
    honors: list[str] = Field(description="荣誉奖项，最多3条")


class Skill(BaseModel):
    """技能"""
    category: Literal["编程语言", "框架/库", "工具/平台", "软技能", "领域知识"] = Field(description="技能类别")
    items: list[str] = Field(description="具体技能，最多10条")
    proficiency: Literal["精通", "熟练", "了解"] = Field(description="熟练程度")


class ResumeDocument(BaseModel):
    """完整简历结构"""
    personal_info: PersonalInfo
    summary: PersonalSummary
    work_experiences: list[WorkExperience] = Field(description="工作经历，最多5条")
    project_experiences: list[ProjectExperience] = Field(description="项目经历，最多5条")
    education: list[Education]
    skills: list[Skill]
    missing_fields: list[str] = Field(description="待补充字段")
    suggestions: list[str] = Field(description="改进建议，最多5条")
    raw_text: Optional[str] = Field(description="Markdown格式完整简历")


class OptimizationType(BaseModel):
    """优化类型"""
    category: Literal["结构调整", "内容强化", "关键词植入", "量化改进", "格式优化"] = Field(description="优化类别")
    description: str = Field(description="优化说明")
    before: Optional[str] = Field(description="优化前内容")
    after: str = Field(description="优化后内容")
    reason: str = Field(description="优化原因")


class JDAlignment(BaseModel):
    """JD对齐分析"""
    jd_requirement: str = Field(description="JD中的要求")
    resume_match: str = Field(description="简历中的匹配点")
    alignment_strength: Literal["强匹配", "弱匹配", "无匹配"] = Field(description="匹配强度")
    suggestion: Optional[str] = Field(description="优化建议")


class OptimizationNotes(BaseModel):
    """优化说明"""
    optimization_types: list[OptimizationType] = Field(description="各类优化，最多10条")
    jd_alignments: list[JDAlignment] = Field(description="JD对齐分析，最多10条")
    keywords_added: list[str] = Field(description="植入的关键词")
    quantified_improvements: list[str] = Field(description="量化改进点")
    overall_score_before: int = Field(description="优化前评分（1-10）")
    overall_score_after: int = Field(description="优化后评分（1-10）")
    improvement_summary: str = Field(description="整体改进摘要")
    user_review_needed: list[str] = Field(description="需用户审核的改动")
    authenticity_check: list[str] = Field(description="真实性校验提醒")


class OptimizedResume(BaseModel):
    """优化后的简历及说明"""
    resume: ResumeDocument
    optimization_notes: OptimizationNotes