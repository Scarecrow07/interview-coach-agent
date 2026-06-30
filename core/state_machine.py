from enum import Enum, auto
from typing import Dict, List


class StepState(Enum):
    """步骤执行状态"""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()


class InterviewFlow(Enum):
    """流程步骤定义"""
    INIT = "init"
    RESUME_PREP = "resume_prep"
    RESUME_OPTIMIZE = "resume_optimize"
    JD_ANALYSIS = "jd_analysis"
    RESUME_ANALYSIS = "resume_analysis"
    MATCH_ANALYSIS = "match_analysis"
    INTERVIEW_PLAN = "interview_plan"
    WRITTEN_TEST = "written_test"
    FINAL_OUTPUT = "final_output"


# 流程流转路径
FLOW_TRANSITIONS: Dict[InterviewFlow, List[InterviewFlow]] = {
    InterviewFlow.INIT: [InterviewFlow.RESUME_PREP],
    InterviewFlow.RESUME_PREP: [InterviewFlow.RESUME_OPTIMIZE, InterviewFlow.JD_ANALYSIS],
    InterviewFlow.RESUME_OPTIMIZE: [InterviewFlow.JD_ANALYSIS],
    InterviewFlow.JD_ANALYSIS: [InterviewFlow.RESUME_ANALYSIS],
    InterviewFlow.RESUME_ANALYSIS: [InterviewFlow.MATCH_ANALYSIS],
    InterviewFlow.MATCH_ANALYSIS: [InterviewFlow.INTERVIEW_PLAN, InterviewFlow.WRITTEN_TEST],
    InterviewFlow.INTERVIEW_PLAN: [InterviewFlow.WRITTEN_TEST, InterviewFlow.FINAL_OUTPUT],
    InterviewFlow.WRITTEN_TEST: [InterviewFlow.FINAL_OUTPUT],
    InterviewFlow.FINAL_OUTPUT: [],
}

# 数据依赖关系
DEPENDENCY_CHAIN: Dict[str, List[str]] = {
    "resume": ["resume_analysis", "match_analysis", "interview_plan"],
    "jd": ["jd_analysis", "resume_analysis", "match_analysis", "interview_plan", "written_test"],
    "jd_report": ["resume_analysis", "match_analysis", "interview_plan", "written_test"],
    "resume_report": ["match_analysis", "interview_plan"],
    "match_report": ["interview_plan", "written_test"],
}