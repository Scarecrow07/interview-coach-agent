"""Models package - Pydantic schemas for structured outputs"""

from .resume_schema import (
    ResumeDocument, PersonalInfo, PersonalSummary, 
    WorkExperience, ProjectExperience, Education, Skill, STARAchievement
)
from .resume_schema import OptimizedResume, OptimizationNotes
from .jd_schema import JDAnalysisResult, ResponsibilityItem, HardRequirement, InterviewQuestion
from .match_schema import MatchAnalysisResult, MatchItem, GapAnalysis
from .qa_schema import QABank, QAPair

__all__ = [
    # Resume
    "ResumeDocument", "PersonalInfo", "PersonalSummary", 
    "WorkExperience", "ProjectExperience", "Education", "Skill", "STARAchievement",
    "OptimizedResume", "OptimizationNotes",
    # JD
    "JDAnalysisResult", "ResponsibilityItem", "HardRequirement", "InterviewQuestion",
    # Match
    "MatchAnalysisResult", "MatchItem", "GapAnalysis",
    # QA
    "QABank", "QAPair",
]