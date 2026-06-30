import re
from typing import Dict, Tuple


class PrivacyProtector:
    """隐私保护处理器"""
    
    SENSITIVE_PATTERNS = {
        "phone": r"1[3-9]\d{9}",
        "id_card": r"\d{17}[\dXx]",
        "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "bank_card": r"\d{16,19}",
    }
    
    def sanitize(self, text: str) -> Tuple[str, Dict[str, str]]:
        """脱敏处理"""
        mappings = {}
        sanitized = text
        
        for type_name, pattern in self.SENSITIVE_PATTERNS.items():
            matches = re.findall(pattern, text)
            for idx, match in enumerate(matches, 1):
                placeholder = f"<{type_name.upper()}_{idx}>"
                sanitized = sanitized.replace(match, placeholder)
                mappings[placeholder] = match
        
        return sanitized, mappings
    
    def restore(self, text: str, mappings: Dict[str, str]) -> str:
        """恢复脱敏内容"""
        restored = text
        for placeholder, original in mappings.items():
            restored = restored.replace(placeholder, original)
        return restored


# 全局隐私保护实例
privacy = PrivacyProtector()


def process_input(user_input: str, session_state: Dict) -> str:
    """处理用户输入"""
    sanitized, mappings = privacy.sanitize(user_input)
    session_state["user_data"]["privacy_mappings"] = mappings
    return sanitized


def prepare_output(output: str, session_state: Dict) -> str:
    """准备输出"""
    mappings = session_state["user_data"].get("privacy_mappings", {})
    return privacy.restore(output, mappings)