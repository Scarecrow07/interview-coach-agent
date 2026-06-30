import asyncio
from typing import Any, Callable, Dict, List, Optional, Tuple

from .state_machine import InterviewFlow, FLOW_TRANSITIONS
from .session_manager import SessionStateManager


class FlowController:
    """流程编排控制器"""
    
    def __init__(self, session_manager: SessionStateManager):
        self.session_manager = session_manager
        self.step_handlers: Dict[InterviewFlow, Callable] = {}
    
    def register_handler(self, step: InterviewFlow, handler: Callable):
        """注册步骤处理器"""
        self.step_handlers[step] = handler
    
    def can_proceed(self, current_step: InterviewFlow, target_step: InterviewFlow) -> bool:
        """检查流转是否允许"""
        allowed_next = FLOW_TRANSITIONS.get(current_step, [])
        return target_step in allowed_next
    
    def get_required_inputs(self, step: InterviewFlow) -> List[str]:
        """获取步骤所需输入数据键"""
        REQUIREMENTS = {
            InterviewFlow.RESUME_OPTIMIZE: ["resume"],
            InterviewFlow.JD_ANALYSIS: ["jd"],
            InterviewFlow.RESUME_ANALYSIS: ["resume", "jd_report"],
            InterviewFlow.MATCH_ANALYSIS: ["jd_report", "resume_report"],
            InterviewFlow.INTERVIEW_PLAN: ["resume_report", "jd_report", "match_report"],
            InterviewFlow.WRITTEN_TEST: ["jd_report", "match_report"],
        }
        return REQUIREMENTS.get(step, [])
    
    def check_prerequisites(self, state: Dict[str, Any], step: InterviewFlow) -> Tuple[bool, List[str]]:
        """检查前置条件是否满足"""
        required = self.get_required_inputs(step)
        
        # 区分必需和可选
        required_keys = [k for k in required if k != "jd_report"]
        optional_keys = [k for k in required if k == "jd_report"]
        
        missing_required = [k for k in required_keys
                          if k not in state["user_data"] and k not in state["analysis_results"]]
        missing_optional = [k for k in optional_keys if k not in state["analysis_results"]]
        
        is_ready = len(missing_required) == 0
        return is_ready, missing_required + missing_optional
    
    async def execute_step(self, session_id: str, step: InterviewFlow) -> Tuple[bool, Optional[str]]:
        """执行指定步骤"""
        state = self.session_manager.get_session(session_id)
        if not state:
            return False, "Session not found"
        
        # 检查前置
        is_ready, missing = self.check_prerequisites(state, step)
        if not is_ready:
            return False, f"缺少前置数据: {missing}"
        
        # 检查是否允许流转
        if not self.can_proceed(state["current_step"], step):
            return False, f"不允许从 {state['current_step'].value} 跳转到 {step.value}"
        
        # 标记执行中
        state["step_states"][step.value] = "IN_PROGRESS"
        self.session_manager._save_session(state)
        
        # 执行处理器
        handler = self.step_handlers.get(step)
        if not handler:
            return False, f"未注册 {step.value} 的处理器"
        
        try:
            result = await handler(state)
            
            # 标记完成，保存结果
            state["step_states"][step.value] = "COMPLETED"
            state["current_step"] = step
            self.session_manager.save_result(session_id, step.value, result)
            
            return True, None
        except Exception as e:
            state["step_states"][step.value] = "FAILED"
            self.session_manager._save_session(state)
            return False, str(e)