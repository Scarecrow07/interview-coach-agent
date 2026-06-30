"""
智能面试准备 Agent - Streamlit 网页应用
"""

import os
import asyncio
import streamlit as st
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="面试作战指挥官",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化服务
from core import (
    SessionStateManager, FlowController, InterviewFlow, StepState,
    FLOW_TRANSITIONS, privacy
)
from services import (
    create_resume_from_background, parse_resume_to_structured, optimize_resume,
    analyze_jd, analyze_resume, analyze_match,
    interview_engine, generate_written_test
)

# 全局实例
session_manager = SessionStateManager()
flow_controller = FlowController(session_manager)


def get_or_create_session() -> str:
    """获取或创建会话"""
    session_id = st.query_params.get("session_id")
    if session_id:
        state = session_manager.get_session(session_id)
        if state:
            return session_id
    
    new_id = session_manager.create_session()
    st.query_params["session_id"] = new_id
    return new_id


def render_progress(state: dict):
    """渲染进度条"""
    steps_order = [
        InterviewFlow.RESUME_PREP,
        InterviewFlow.JD_ANALYSIS,
        InterviewFlow.RESUME_ANALYSIS,
        InterviewFlow.MATCH_ANALYSIS,
        InterviewFlow.INTERVIEW_PLAN,
    ]
    
    completed_count = sum(
        1 for step in steps_order
        if state["step_states"].get(step.value) == StepState.COMPLETED.value
    )
    
    st.progress(completed_count / len(steps_order))
    
    col_width = len(steps_order)
    cols = st.columns(col_width)
    
    for i, step in enumerate(steps_order):
        step_state = state["step_states"].get(step.value)
        with cols[i]:
            if step_state == StepState.COMPLETED.value:
                st.markdown(f"✅ {step.value}")
            elif step_state == StepState.IN_PROGRESS.value:
                st.markdown(f"⏳ {step.value}")
            else:
                st.markdown(f"⏸ {step.value}")


def render_sidebar(session_id: str, state: dict):
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("### 🎯 面试作战指挥官")
        st.markdown(f"**会话 ID**: `{session_id[:8]}...`")
        
        render_progress(state)
        
        st.markdown("---")
        
        # 显示当前数据
        st.markdown("### 已准备数据")
        if state["user_data"]:
            for key, value in state["user_data"].items():
                if key == "resume":
                    st.markdown("✅ 简历已准备")
                elif key == "jd":
                    st.markdown("✅ JD已准备")
        else:
            st.markdown("暂无数据")
        
        st.markdown("---")
        
        # 操作按钮
        if st.button("🔄 重置会话"):
            session_manager.delete_session(session_id)
            st.query_params.clear()
            st.rerun()


def render_resume_prep(session_id: str, state: dict):
    """渲染简历准备界面"""
    st.markdown("### 📝 简历准备")
    
    choice = st.radio(
        "请选择简历准备方式：",
        ["上传已有简历", "填写信息创建新简历"],
        horizontal=True
    )
    
    if choice == "上传已有简历":
        uploaded_text = st.text_area(
            "请粘贴简历内容：",
            height=300,
            placeholder="粘贴简历文本..."
        )
        
        if st.button("解析简历", type="primary"):
            if uploaded_text.strip():
                with st.spinner("解析中..."):
                    # 脱敏处理
                    sanitized, mappings = privacy.sanitize(uploaded_text)
                    
                    # 解析简历
                    parsed = parse_resume_to_structured(sanitized)
                    
                    # 保存
                    session_manager.update_user_data(session_id, "resume_choice", "upload")
                    session_manager.update_user_data(session_id, "resume_raw", uploaded_text)
                    session_manager.save_result(session_id, "resume", parsed)
                    
                    st.success("简历解析完成！")
                    st.rerun()
            else:
                st.error("请输入简历内容")
    
    elif choice == "填写信息创建新简历":
        background = st.text_area(
            "请描述您的背景（学习经历、工作经验、项目经验、个人优势等）：",
            height=200,
            placeholder="例如：我是一名有5年经验的前端工程师，曾在XX公司负责..."
        )
        
        if st.button("创建简历", type="primary"):
            if background.strip():
                with st.spinner("创建中..."):
                    created = create_resume_from_background(background)
                    
                    session_manager.update_user_data(session_id, "resume_choice", "create")
                    session_manager.update_user_data(session_id, "user_background", background)
                    session_manager.save_result(session_id, "resume", created)
                    
                    st.success("简历创建完成！")
                    st.rerun()
            else:
                st.error("请输入背景描述")


def render_resume_display(state: dict):
    """显示简历"""
    resume = state["analysis_results"].get("resume")
    if resume:
        st.markdown("### 📄 当前简历")
        
        with st.expander("查看简历详情", expanded=True):
            # 显示关键信息
            st.markdown(f"**姓名**: {resume.personal_info.name}")
            st.markdown(f"**核心身份**: {resume.summary.core_identity}")
            st.markdown(f"**工作年限**: {resume.summary.years_experience}年")
            
            # 技能
            st.markdown("**技能**:")
            for skill in resume.skills[:3]:
                st.markdown(f"- {skill.category}: {', '.join(skill.items[:5])}")
            
            # 工作经历
            st.markdown("**工作经历**:")
            for exp in resume.work_experiences[:2]:
                st.markdown(f"- {exp.company} - {exp.position}")
            
            # 待补充字段
            if resume.missing_fields:
                st.warning(f"待补充字段: {', '.join(resume.missing_fields[:5])}")
        
        # 显示完整简历
        if resume.raw_text:
            with st.expander("查看完整简历 (Markdown)"):
                st.markdown(resume.raw_text)


def render_jd_input(session_id: str, state: dict):
    """渲染 JD 输入界面"""
    st.markdown("### 📋 JD 分析")
    
    jd_text = st.text_area(
        "请输入目标职位 JD：",
        height=300,
        placeholder="粘贴职位描述..."
    )
    
    if st.button("分析 JD", type="primary"):
        if jd_text.strip():
            with st.spinner("分析中..."):
                jd_report = analyze_jd(jd_text)
                
                session_manager.update_user_data(session_id, "jd", jd_text)
                session_manager.save_result(session_id, "jd_report", jd_report)
                
                st.success("JD 分析完成！")
                st.rerun()
        else:
            st.error("请输入 JD 内容")


def render_jd_display(state: dict):
    """显示 JD 分析结果"""
    jd_report = state["analysis_results"].get("jd_report")
    if jd_report:
        st.markdown("### 📋 JD 分析报告")
        
        with st.expander("查看分析详情", expanded=True):
            # 岗位画像
            st.markdown("**岗位画像**:")
            job_profile = jd_report.job_profile
            for key, value in list(job_profile.items())[:3]:
                st.markdown(f"- {key}: {value}")
            
            # 核心职责
            st.markdown("**核心职责**:")
            for resp in jd_report.core_responsibilities[:3]:
                st.markdown(f"- {resp.responsibility} ({resp.priority})")
            
            # 硬性要求
            st.markdown("**硬性要求**:")
            for req in jd_report.hard_requirements[:3]:
                st.markdown(f"- {req.requirement} [{req.type}]")
            
            # 面试高频问题
            st.markdown("**面试高频问题预测**:")
            for q in jd_report.interview_questions:
                st.markdown(f"- [{q.category}] {q.question} ({q.difficulty})")


def render_resume_analysis(session_id: str, state: dict):
    """渲染简历分析"""
    st.markdown("### 🔍 简历分析")
    
    resume = state["analysis_results"].get("resume")
    jd_report = state["analysis_results"].get("jd_report")
    
    if not resume:
        st.error("请先准备简历")
        return
    
    if jd_report:
        st.info("将结合 JD 进行针对性分析")
    else:
        st.info("将进行通用简历分析")
    
    if st.button("分析简历", type="primary"):
        with st.spinner("分析中..."):
            resume_report = analyze_resume(resume, jd_report)
            session_manager.save_result(session_id, "resume_report", resume_report)
            st.success("简历分析完成！")
            st.rerun()


def render_resume_analysis_display(state: dict):
    """显示简历分析结果"""
    resume_report = state["analysis_results"].get("resume_report")
    if resume_report:
        st.markdown("### 🔍 简历分析报告")
        
        with st.expander("查看分析详情", expanded=True):
            # 摘要
            st.markdown("**简历摘要**:")
            st.markdown(resume_report.summary)
            
            # 成就事件
            st.markdown("**核心成就**:")
            for ach in resume_report.achievements[:3]:
                st.markdown(f"- {ach.event_name}")
            
            # 优势
            st.markdown("**核心优势**:")
            for adv in resume_report.advantages[:3]:
                st.markdown(f"- {adv.advantage}")
            
            # 风险
            if resume_report.risks:
                st.markdown("**风险识别**:")
                for risk in resume_report.risks[:3]:
                    st.markdown(f"- {risk.description} [{risk.severity}]")


def render_match_analysis(session_id: str, state: dict):
    """渲染匹配度分析"""
    st.markdown("### 📊 匹配度分析")
    
    jd_report = state["analysis_results"].get("jd_report")
    resume_report = state["analysis_results"].get("resume_report")
    
    if not jd_report or not resume_report:
        st.error("请先完成 JD 分析和简历分析")
        return
    
    if st.button("分析匹配度", type="primary"):
        with st.spinner("分析中..."):
            match_report = analyze_match(jd_report, resume_report)
            session_manager.save_result(session_id, "match_report", match_report)
            st.success("匹配度分析完成！")
            st.rerun()


def render_match_display(state: dict):
    """显示匹配度分析结果"""
    match_report = state["analysis_results"].get("match_report")
    if match_report:
        st.markdown("### 📊 匹配度报告")
        
        # 整体匹配度
        overall = match_report.overall_score
        st.metric("整体匹配度", overall.get("percentage", "N/A"))
        
        with st.expander("查看详细分析", expanded=True):
            # 能力匹配明细
            st.markdown("**能力匹配明细**:")
            for item in match_report.capability_match[:5]:
                status_color = {
                    "强匹配": "🟢",
                    "弱匹配": "🟡",
                    "不匹配": "🔴"
                }.get(item.match_status, "⚪")
                st.markdown(f"- {status_color} {item.capability}: {item.match_status}")
            
            # 差距分析
            st.markdown("**差距弥补方案**:")
            for gap in match_report.gap_analysis[:3]:
                st.markdown(f"- {gap.gap}: {gap.solution}")
            
            # 核心优势
            st.markdown("**核心优势强化**:")
            for adv in match_report.core_advantages:
                st.markdown(f"- {adv}")


def render_interview_plan(session_id: str, state: dict):
    """渲染面试方案生成"""
    st.markdown("### 🎯 面试方案生成")
    
    resume_report = state["analysis_results"].get("resume_report")
    jd_report = state["analysis_results"].get("jd_report")
    match_report = state["analysis_results"].get("match_report")
    
    if not resume_report or not jd_report or not match_report:
        st.error("请先完成前置分析")
        return
    
    if st.button("生成面试方案", type="primary"):
        with st.spinner("生成中...（并行生成三部分，请耐心等待）"):
            interview_plan = asyncio.run(
                interview_engine.generate_interview_plan_parallel(
                    resume_report, jd_report, match_report
                )
            )
            session_manager.save_result(session_id, "interview_plan", interview_plan)
            st.success("面试方案生成完成！")
            st.rerun()


def render_interview_plan_display(state: dict):
    """显示面试方案"""
    interview_plan = state["analysis_results"].get("interview_plan")
    if interview_plan:
        st.markdown("### 🎯 面试作战方案")
        
        # 自我介绍
        intro = interview_plan.get("self_introduction", {})
        if intro:
            with st.expander("📝 自我介绍", expanded=True):
                st.markdown(f"**一句话介绍**: {intro.get('brief_intro', '')}")
                st.markdown(f"**标准介绍**: {intro.get('standard_intro', '')}")
                st.markdown("**关键要点**:")
                for pt in intro.get("key_points", [])[:5]:
                    st.markdown(f"- {pt}")
        
        # 项目介绍
        projects = interview_plan.get("project_introductions", [])
        if projects:
            with st.expander("💼 项目介绍"):
                for proj in projects[:3]:
                    st.markdown(f"**{proj.get('project_name', '')}**")
                    st.markdown(f"- {proj.get('brief_intro', '')}")
        
        # 问答库
        qa_bank = interview_plan.get("qa_bank")
        if qa_bank:
            with st.expander("❓ 问答库 (15题)"):
                questions = qa_bank.questions if hasattr(qa_bank, 'questions') else qa_bank.get("questions", [])
                for qa in questions[:10]:
                    priority_icon = {
                        "高频必答": "🔥",
                        "常规题": "📌",
                        "补充题": "💡"
                    }.get(qa.priority if hasattr(qa, 'priority') else qa.get("priority", ""), "❓")
                    st.markdown(f"**{priority_icon} {qa.question if hasattr(qa, 'question') else qa.get('question', '')}**")
                    st.markdown(f"[{qa.category if hasattr(qa, 'category') else qa.get('category', '')}]")


def render_written_test(session_id: str, state: dict):
    """渲染笔试题目生成"""
    st.markdown("### 📝 笔试题目（可选）")
    
    jd_report = state["analysis_results"].get("jd_report")
    match_report = state["analysis_results"].get("match_report")
    
    if not jd_report:
        st.error("请先完成 JD 分析")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("生成笔试题目"):
            with st.spinner("生成中..."):
                written_test = generate_written_test(jd_report, match_report)
                session_manager.save_result(session_id, "written_test", written_test)
                st.success("笔试题目生成完成！")
                st.rerun()
    
    # 显示已生成的笔试题目
    written_test = state["analysis_results"].get("written_test")
    if written_test:
        with col2:
            with st.expander("查看笔试题目"):
                questions = written_test.get("questions", [])
                for q in questions:
                    st.markdown(f"**{q.get('id', '')}: {q.get('title', '')}**")
                    st.markdown(f"[{q.get('category', '')}] {q.get('difficulty', '')} - {q.get('time_estimate', '')}")


def render_final_manual(state: dict):
    """渲染最终手册"""
    st.markdown("### 📚 最终面试作战手册")
    
    # 检查所有结果
    resume = state["analysis_results"].get("resume")
    jd_report = state["analysis_results"].get("jd_report")
    resume_report = state["analysis_results"].get("resume_report")
    match_report = state["analysis_results"].get("match_report")
    interview_plan = state["analysis_results"].get("interview_plan")
    
    if not all([resume, jd_report, resume_report, match_report, interview_plan]):
        st.error("请先完成所有前置步骤")
        return
    
    if st.button("生成完整手册", type="primary"):
        with st.spinner("整合中..."):
            # 生成手册
            manual = generate_final_manual(state)
            
            # 显示手册
            st.markdown("---")
            st.markdown("### 📚 面试作战手册")
            st.markdown(manual)
            
            # 下载按钮
            st.download_button(
                label="下载手册 (Markdown)",
                data=manual,
                file_name="面试作战手册.md",
                mime="text/markdown"
            )


def generate_final_manual(state: dict) -> str:
    """生成最终手册"""
    resume = state["analysis_results"].get("resume")
    jd_report = state["analysis_results"].get("jd_report")
    resume_report = state["analysis_results"].get("resume_report")
    match_report = state["analysis_results"].get("match_report")
    interview_plan = state["analysis_results"].get("interview_plan")
    
    manual = f"""# 面试作战手册

生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## 一、岗位分析

### 岗位画像
- 岗位名称：{jd_report.job_profile.get('title', 'N/A')}
- 岗位级别：{jd_report.job_profile.get('level', 'N/A')}

### 核心职责
"""
    
    for resp in jd_report.core_responsibilities[:5]:
        manual += f"- {resp.responsibility}\n"
    
    manual += "\n### 硬性要求\n"
    for req in jd_report.hard_requirements[:5]:
        manual += f"- {req.requirement} [{req.type}]\n"
    
    manual += "\n---\n\n## 二、简历分析\n"
    manual += f"\n{resume_report.summary}\n"
    
    manual += "\n### 核心成就\n"
    for ach in resume_report.achievements[:5]:
        manual += f"\n**{ach.event_name}**\n"
        manual += f"- 情境：{ach.star_l.situation}\n"
        manual += f"- 任务：{ach.star_l.task}\n"
        manual += f"- 结果：{ach.star_l.result}\n"
    
    manual += "\n---\n\n## 三、匹配度分析\n"
    manual += f"\n整体匹配度：{match_report.overall_score.get('percentage', 'N/A')}\n"
    
    manual += "\n---\n\n## 四、面试方案\n"
    
    intro = interview_plan.get("self_introduction", {})
    manual += f"\n### 自我介绍\n\n{intro.get('standard_intro', '')}\n"
    
    qa_bank = interview_plan.get("qa_bank")
    if qa_bank:
        manual += "\n### 问答库\n\n"
        questions = qa_bank.questions if hasattr(qa_bank, 'questions') else qa_bank.get("questions", [])
        for qa in questions:
            manual += f"\n**Q: {qa.question if hasattr(qa, 'question') else qa.get('question', '')}**\n\n"
            manual += f"{qa.sample_answer if hasattr(qa, 'sample_answer') else qa.get('sample_answer', '')}\n\n"
    
    manual += "\n---\n\n祝面试顺利！\n"
    
    return manual


def main():
    """主界面"""
    # 获取或创建会话
    session_id = get_or_create_session()
    state = session_manager.get_session(session_id)
    
    if not state:
        session_id = session_manager.create_session()
        st.query_params["session_id"] = session_id
        state = session_manager.get_session(session_id)
    
    # 渲染侧边栏
    render_sidebar(session_id, state)
    
    # 主标题
    st.title("🎯 面试作战指挥官")
    st.markdown("智能面试准备全流程助手")
    
    # 根据当前步骤显示对应界面
    current_step = state["current_step"]
    
    # 创建标签页
    tabs = st.tabs([
        "简历准备",
        "JD分析",
        "简历分析",
        "匹配度",
        "面试方案",
        "笔试题目",
        "最终手册"
    ])
    
    with tabs[0]:  # 简历准备
        resume = state["analysis_results"].get("resume")
        if resume:
            render_resume_display(state)
            
            # 优化简历选项
            col1, col2 = st.columns(2)
            with col1:
                if st.button("重新准备简历"):
                    session_manager.update_user_data(session_id, "resume", None)
                    st.rerun()
        else:
            render_resume_prep(session_id, state)
    
    with tabs[1]:  # JD分析
        jd_report = state["analysis_results"].get("jd_report")
        if jd_report:
            render_jd_display(state)
            if st.button("重新分析 JD"):
                session_manager.update_user_data(session_id, "jd", None)
                st.rerun()
        else:
            render_jd_input(session_id, state)
    
    with tabs[2]:  # 简历分析
        resume_report = state["analysis_results"].get("resume_report")
        if resume_report:
            render_resume_analysis_display(state)
            if st.button("重新分析简历"):
                st.rerun()
        else:
            render_resume_analysis(session_id, state)
    
    with tabs[3]:  # 匹配度
        match_report = state["analysis_results"].get("match_report")
        if match_report:
            render_match_display(state)
            if st.button("重新分析匹配度"):
                st.rerun()
        else:
            render_match_analysis(session_id, state)
    
    with tabs[4]:  # 面试方案
        interview_plan = state["analysis_results"].get("interview_plan")
        if interview_plan:
            render_interview_plan_display(state)
            if st.button("重新生成面试方案"):
                st.rerun()
        else:
            render_interview_plan(session_id, state)
    
    with tabs[5]:  # 笔试题目
        render_written_test(session_id, state)
    
    with tabs[6]:  # 最终手册
        render_final_manual(state)


if __name__ == "__main__":
    main()