#!/usr/bin/env python3
"""
智能面试准备 Agent - 主入口
"""

import os

# 设置环境变量（如果未设置）
if "DEEPSEEK_API_KEY" not in os.environ:
    print("请设置环境变量 DEEPSEEK_API_KEY")
    print("示例: export DEEPSEEK_API_KEY='your_key'")
    exit(1)

from config import settings, setup_logging
from core import SessionStateManager, FlowController, InterviewFlow
from services.llm_client import llm

logger = setup_logging()


def main():
    """主入口"""
    logger.info(f"启动面试准备Agent，使用模型: {settings.DEEPSEEK_MODEL}")
    
    # 创建会话管理器和流程控制器
    session_manager = SessionStateManager()
    flow_controller = FlowController(session_manager)
    
    # 创建示例会话
    session_id = session_manager.create_session()
    logger.info(f"创建会话: {session_id}")
    
    # 获取会话状态
    state = session_manager.get_session(session_id)
    logger.info(f"当前步骤: {state['current_step'].value}")
    
    print("\n面试准备Agent已启动！")
    print(f"会话ID: {session_id}")
    print(f"当前步骤: {state['current_step'].value}")
    print("\n下一步请启动 Streamlit 界面:")
    print("  streamlit run api/streamlit_app.py")


if __name__ == "__main__":
    main()