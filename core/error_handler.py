from enum import Enum
import time
from typing import Any, Callable, Optional, Tuple

from .state_machine import InterviewFlow


class ErrorType(Enum):
    """错误类型"""
    API_KEY_INVALID = "api_key_invalid"
    NETWORK_TIMEOUT = "network_timeout"
    RATE_LIMIT = "rate_limit"
    MODEL_ERROR = "model_error"


class ErrorHandler:
    """统一错误处理"""
    
    MAX_RETRIES = 3
    RETRY_INTERVAL = 2.0
    
    def classify_error(self, exception: Exception) -> ErrorType:
        """错误分类"""
        msg = str(exception).lower()
        if "api key" in msg or "invalid key" in msg or "401" in msg:
            return ErrorType.API_KEY_INVALID
        if "timeout" in msg or "network" in msg:
            return ErrorType.NETWORK_TIMEOUT
        if "rate limit" in msg or "429" in msg:
            return ErrorType.RATE_LIMIT
        return ErrorType.MODEL_ERROR
    
    def retry_call(self, func: Callable, *args, **kwargs) -> Tuple[Any, Optional[ErrorType]]:
        """带重试的调用"""
        for attempt in range(self.MAX_RETRIES):
            try:
                result = func(*args, **kwargs)
                return result, None
            except Exception as e:
                error_type = self.classify_error(e)
                
                # API Key错误不重试
                if error_type == ErrorType.API_KEY_INVALID:
                    return None, error_type
                
                # 限流加倍等待
                if error_type == ErrorType.RATE_LIMIT:
                    wait_time = self.RETRY_INTERVAL * (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                
                # 其他错误重试
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_INTERVAL)
                    continue
                
                return None, error_type
        
        return None, ErrorType.MODEL_ERROR
    
    def handle_missing_dependency(self, step: InterviewFlow, missing_key: str) -> Tuple[bool, str]:
        """处理依赖缺失的降级策略"""
        # 简历分析缺失JD报告：降级为通用分析
        if step == InterviewFlow.RESUME_ANALYSIS and missing_key == "jd_report":
            return True, "JD分析暂时不可用，将对简历进行通用分析。"
        
        # 匹配度分析缺失必需报告：无法降级
        if step == InterviewFlow.MATCH_ANALYSIS:
            if missing_key in ["jd_report", "resume_report"]:
                return False, f"缺少必需数据{missing_key}，请先完成前置步骤。"
        
        return False, f"缺少前置数据：{missing_key}"


# 全局错误处理器
error_handler = ErrorHandler()