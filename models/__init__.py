from .resume_schema import ResumeDocument, PersonalInfo, PersonalSummary, WorkExperience, ProjectExperience, Education, Skill, STARAchievement
from .jd_schema import JDAnalysisResult, ResponsibilityItem, HardRequirement, InterviewQuestion
from .match_schema import MatchAnalysisResult, MatchItem, GapAnalysis
from .qa_schema import QABank, QAPair

__all__ = [
    # Resume
    "ResumeDocument", "PersonalInfo", "PersonalSummary", "WorkExperience",
    "ProjectExperience", "Education", "Skill", "STARAchievement",
    # JD
    "JDAnalysisResult", "ResponsibilityItem", "HardRequirement", "InterviewQuestion",
    # Match
    "MatchAnalysisResult", "MatchItem", "GapAnalysis",
    # QA
    "QABank", "QAPair",
]