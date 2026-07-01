"""
简历 PDF 生成服务

支持将 ResumeDocument / OptimizedResume 渲染为专业排版的 PDF 文件，
供 Streamlit 应用或 FastAPI 后端导出/下载使用。
"""

import io
import os
import platform
from typing import Optional, Union

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, ListFlowable, ListItem
)

from models.resume_schema import (
    ResumeDocument, OptimizedResume, PersonalInfo, PersonalSummary,
    WorkExperience, ProjectExperience, Education, Skill, STARAchievement,
)

# ──────────────────────────────────────────────
# 颜色常量
# ──────────────────────────────────────────────
PRIMARY_COLOR = HexColor("#1a365d")     # 深蓝
ACCENT_COLOR = HexColor("#2b6cb0")      # 中蓝
LIGHT_BG = HexColor("#f7fafc")          # 浅灰蓝背景
TEXT_COLOR = HexColor("#2d3748")        # 正文深灰
MUTED_COLOR = HexColor("#718096")       # 次要文字
DIVIDER_COLOR = HexColor("#e2e8f0")     # 分割线

# ──────────────────────────────────────────────
# 页面尺寸
# ──────────────────────────────────────────────
PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 18 * mm
RIGHT_MARGIN = 18 * mm
TOP_MARGIN = 16 * mm
BOTTOM_MARGIN = 16 * mm
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN


# ──────────────────────────────────────────────
# CJK 字体注册
# ──────────────────────────────────────────────
_cjk_font_registered = False
CJK_FONT_NAME = "Helvetica"


def _register_cjk_font():
    """注册支持中文的字体，按操作系统自动查找"""
    global _cjk_font_registered, CJK_FONT_NAME

    if _cjk_font_registered:
        return CJK_FONT_NAME

    system = platform.system()

    if system == "Darwin":  # macOS
        candidates = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    elif system == "Windows":
        candidates = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/simhei.ttf",
        ]
    else:  # Linux
        candidates = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        ]

    for font_path in candidates:
        if os.path.exists(font_path):
            try:
                # .ttc 文件需要指定 subfontIndex
                if font_path.endswith(".ttc"):
                    pdfmetrics.registerFont(
                        TTFont("CJKFont", font_path, subfontIndex=0)
                    )
                else:
                    pdfmetrics.registerFont(TTFont("CJKFont", font_path))
                CJK_FONT_NAME = "CJKFont"
                _cjk_font_registered = True
                return CJK_FONT_NAME
            except Exception:
                continue

    # 如果找不到 CJK 字体，回退到 Helvetica（中文可能显示异常）
    _cjk_font_registered = True
    return CJK_FONT_NAME


# ──────────────────────────────────────────────
# 文本规范化
# ──────────────────────────────────────────────
_DASH_MAP = {
    "\u2010": "-", "\u2011": "-", "\u2012": "-",
    "\u2013": "-", "\u2014": "-", "\u2015": "-",
    "\u2212": "-", "\u00ad": "-",
}


def _normalize(text: str) -> str:
    """规范化特殊 Unicode 字符"""
    if not text:
        return ""
    for old, new in _DASH_MAP.items():
        text = text.replace(old, new)
    return text


# ──────────────────────────────────────────────
# 样式定义
# ──────────────────────────────────────────────
def _build_styles(font_name: str) -> dict:
    """构建简历 PDF 所需的所有段落样式"""

    return {
        # 顶部姓名
        "name": ParagraphStyle(
            "Name", fontName=font_name, fontSize=22, leading=28,
            textColor=PRIMARY_COLOR, alignment=TA_LEFT, wordWrap="CJK",
        ),
        # 联系信息
        "contact": ParagraphStyle(
            "Contact", fontName=font_name, fontSize=9, leading=13,
            textColor=MUTED_COLOR, alignment=TA_LEFT, wordWrap="CJK",
        ),
        # 章节标题
        "section": ParagraphStyle(
            "Section", fontName=font_name, fontSize=13, leading=18,
            textColor=ACCENT_COLOR, spaceBefore=14, spaceAfter=6,
            wordWrap="CJK",
        ),
        # 子标题（公司/项目名/学校）
        "subtitle": ParagraphStyle(
            "Subtitle", fontName=font_name, fontSize=11, leading=15,
            textColor=PRIMARY_COLOR, spaceBefore=8, spaceAfter=2,
            wordWrap="CJK",
        ),
        # 日期行
        "daterow": ParagraphStyle(
            "DateRow", fontName=font_name, fontSize=9, leading=12,
            textColor=MUTED_COLOR, spaceAfter=4, wordWrap="CJK",
        ),
        # 正文
        "body": ParagraphStyle(
            "Body", fontName=font_name, fontSize=10, leading=15,
            textColor=TEXT_COLOR, spaceAfter=4, wordWrap="CJK",
            alignment=TA_JUSTIFY,
        ),
        # 列表项
        "bullet": ParagraphStyle(
            "Bullet", fontName=font_name, fontSize=10, leading=14,
            textColor=TEXT_COLOR, spaceAfter=2, wordWrap="CJK",
            leftIndent=12, bulletIndent=2,
        ),
        # 个人总结
        "summary": ParagraphStyle(
            "Summary", fontName=font_name, fontSize=10, leading=16,
            textColor=TEXT_COLOR, spaceAfter=4, wordWrap="CJK",
            alignment=TA_JUSTIFY,
        ),
        # 技能标签
        "skill_cat": ParagraphStyle(
            "SkillCat", fontName=font_name, fontSize=10, leading=14,
            textColor=PRIMARY_COLOR, wordWrap="CJK",
        ),
        # 优化说明
        "opt_note": ParagraphStyle(
            "OptNote", fontName=font_name, fontSize=9, leading=13,
            textColor=MUTED_COLOR, spaceAfter=3, wordWrap="CJK",
        ),
        # 高亮关键词
        "highlight": ParagraphStyle(
            "Highlight", fontName=font_name, fontSize=9, leading=12,
            textColor=ACCENT_COLOR, wordWrap="CJK",
        ),
    }


# ──────────────────────────────────────────────
# 分割线
# ──────────────────────────────────────────────
def _section_divider() -> HRFlowable:
    """章节分割线"""
    return HRFlowable(
        width="100%", thickness=1.2, color=ACCENT_COLOR,
        spaceBefore=2, spaceAfter=8,
    )


def _thin_divider() -> HRFlowable:
    """细分割线"""
    return HRFlowable(
        width="100%", thickness=0.5, color=DIVIDER_COLOR,
        spaceBefore=4, spaceAfter=4,
    )


# ──────────────────────────────────────────────
# 各章节渲染
# ──────────────────────────────────────────────
def _render_header(info: PersonalInfo, styles: dict) -> list:
    """渲染顶部：姓名 + 联系方式"""
    story = []

    # 姓名
    story.append(Paragraph(_normalize(info.name), styles["name"]))

    # 联系信息行
    contact_parts = []
    if info.phone:
        contact_parts.append(info.phone)
    if info.email:
        contact_parts.append(info.email)
    if info.location:
        contact_parts.append(info.location)
    if info.linkedin:
        contact_parts.append(f"LinkedIn: {info.linkedin}")
    if info.github:
        contact_parts.append(f"GitHub: {info.github}")

    if contact_parts:
        contact_text = "  |  ".join(contact_parts)
        story.append(Spacer(1, 2))
        story.append(Paragraph(_normalize(contact_text), styles["contact"]))

    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_COLOR, spaceAfter=4))

    return story


def _render_summary(summary: PersonalSummary, styles: dict) -> list:
    """渲染个人总结"""
    story = []

    story.append(Paragraph("个人总结", styles["section"]))
    story.append(_section_divider())

    # 核心身份
    story.append(Paragraph(
        f"<b>{_normalize(summary.core_identity)}</b>"
        f"  |  {summary.years_experience}年经验",
        styles["body"],
    ))

    # 价值主张
    if summary.value_proposition:
        story.append(Paragraph(_normalize(summary.value_proposition), styles["summary"]))

    # 核心领域
    if summary.key_domains:
        domains_text = "  ".join(
            f'<font color="#2b6cb0"><b>{d}</b></font>'
            for d in summary.key_domains
        )
        story.append(Paragraph(f"核心领域: {domains_text}", styles["body"]))

    # 亮点关键词
    if summary.highlights:
        tags = "  ".join(
            f'<font color="#2b6cb0">#{h}</font>'
            for h in summary.highlights
        )
        story.append(Paragraph(f"亮点: {tags}", styles["highlight"]))

    return story


def _render_work_experiences(experiences: list[WorkExperience], styles: dict) -> list:
    """渲染工作经历"""
    story = []

    if not experiences:
        return story

    story.append(Paragraph("工作经历", styles["section"]))
    story.append(_section_divider())

    for exp in experiences:
        block = []

        # 公司 + 职位
        block.append(Paragraph(
            f"<b>{_normalize(exp.company)}</b>  -  {_normalize(exp.position)}",
            styles["subtitle"],
        ))

        # 时间
        date_str = exp.start_date
        if exp.end_date:
            date_str += f" ~ {exp.end_date}"
        else:
            date_str += " ~ 至今"
        block.append(Paragraph(date_str, styles["daterow"]))

        # 主要职责
        if exp.responsibilities:
            items = [
                ListItem(Paragraph(_normalize(r), styles["bullet"]),
                         value="circle", leftIndent=14)
                for r in exp.responsibilities
            ]
            block.append(ListFlowable(
                items, bulletType="bullet", bulletColor=ACCENT_COLOR,
                leftIndent=10, spaceAfter=4,
            ))

        # 量化成就
        if exp.achievements:
            block.append(Paragraph("<b>关键成就:</b>", styles["body"]))
            items = [
                ListItem(Paragraph(_normalize(a), styles["bullet"]),
                         value="square", leftIndent=14)
                for a in exp.achievements
            ]
            block.append(ListFlowable(
                items, bulletType="bullet", bulletColor=ACCENT_COLOR,
                leftIndent=10, spaceAfter=4,
            ))

        # 技术栈
        if exp.technologies:
            tech_text = "  ".join(
                f'<font color="#2b6cb0">{t}</font>'
                for t in exp.technologies
            )
            block.append(Paragraph(f"技术栈: {tech_text}", styles["body"]))

        # STAR-L 成就
        if exp.star_achievements:
            for star in exp.star_achievements:
                block.append(Spacer(1, 4))
                block.append(Paragraph(
                    f"<b>STAR-L: {_normalize(star.result)}</b>",
                    styles["body"],
                ))
                block.append(Paragraph(
                    f"<b>情境:</b> {_normalize(star.situation)}",
                    styles["bullet"],
                ))
                block.append(Paragraph(
                    f"<b>任务:</b> {_normalize(star.task)}",
                    styles["bullet"],
                ))
                if star.action:
                    block.append(Paragraph(
                        f"<b>行动:</b> {'; '.join(_normalize(a) for a in star.action)}",
                        styles["bullet"],
                    ))
                block.append(Paragraph(
                    f"<b>结果:</b> {_normalize(star.result)}",
                    styles["bullet"],
                ))
                if star.learning:
                    block.append(Paragraph(
                        f"<b>复盘:</b> {_normalize(star.learning)}",
                        styles["bullet"],
                    ))

        block.append(_thin_divider())
        story.extend(block)

    return story


def _render_project_experiences(projects: list[ProjectExperience], styles: dict) -> list:
    """渲染项目经历"""
    story = []

    if not projects:
        return story

    story.append(Paragraph("项目经历", styles["section"]))
    story.append(_section_divider())

    for proj in projects:
        block = []

        # 项目名 + 角色
        block.append(Paragraph(
            f"<b>{_normalize(proj.project_name)}</b>  -  {_normalize(proj.role)}",
            styles["subtitle"],
        ))

        # 背景与目标
        if proj.background:
            block.append(Paragraph(_normalize(proj.background), styles["body"]))

        # 关键挑战
        if proj.key_challenges:
            block.append(Paragraph("<b>关键挑战:</b>", styles["body"]))
            items = [
                ListItem(Paragraph(_normalize(c), styles["bullet"]),
                         value="circle", leftIndent=14)
                for c in proj.key_challenges
            ]
            block.append(ListFlowable(
                items, bulletType="bullet", bulletColor=ACCENT_COLOR,
                leftIndent=10, spaceAfter=4,
            ))

        # 关键行动
        if proj.actions:
            block.append(Paragraph("<b>关键行动:</b>", styles["body"]))
            items = [
                ListItem(Paragraph(_normalize(a), styles["bullet"]),
                         value="circle", leftIndent=14)
                for a in proj.actions
            ]
            block.append(ListFlowable(
                items, bulletType="bullet", bulletColor=ACCENT_COLOR,
                leftIndent=10, spaceAfter=4,
            ))

        # 结果
        if proj.results:
            block.append(Paragraph(
                f"<b>结果:</b> {_normalize(proj.results)}",
                styles["body"],
            ))

        # 复盘
        if proj.learnings:
            block.append(Paragraph(
                f"<b>复盘:</b> {_normalize(proj.learnings)}",
                styles["body"],
            ))

        # 技术栈
        if proj.technologies:
            tech_text = "  ".join(
                f'<font color="#2b6cb0">{t}</font>'
                for t in proj.technologies
            )
            block.append(Paragraph(f"技术栈: {tech_text}", styles["body"]))

        block.append(_thin_divider())
        story.extend(block)

    return story


def _render_education(educations: list[Education], styles: dict) -> list:
    """渲染教育背景"""
    story = []

    if not educations:
        return story

    story.append(Paragraph("教育背景", styles["section"]))
    story.append(_section_divider())

    for edu in educations:
        block = []

        # 学校 + 学位
        block.append(Paragraph(
            f"<b>{_normalize(edu.school)}</b>  -  {_normalize(edu.degree)}  {_normalize(edu.major)}",
            styles["subtitle"],
        ))

        # 时间
        date_str = f"{edu.start_date} ~ {edu.end_date}"
        block.append(Paragraph(date_str, styles["daterow"]))

        # 荣誉
        if edu.honors:
            items = [
                ListItem(Paragraph(_normalize(h), styles["bullet"]),
                         value="circle", leftIndent=14)
                for h in edu.honors
            ]
            block.append(ListFlowable(
                items, bulletType="bullet", bulletColor=ACCENT_COLOR,
                leftIndent=10, spaceAfter=4,
            ))

        block.append(_thin_divider())
        story.extend(block)

    return story


def _render_skills(skills: list[Skill], styles: dict) -> list:
    """渲染技能（表格形式）"""
    story = []

    if not skills:
        return story

    story.append(Paragraph("专业技能", styles["section"]))
    story.append(_section_divider())

    # 构建表格数据
    table_data = []
    for skill in skills:
        cat = skill.category
        items_text = "、".join(skill.items)
        prof = skill.proficiency

        # 熟练度颜色标记
        prof_color = {
            "精通": "#2b6cb0",
            "熟练": "#38a169",
            "了解": "#718096",
        }.get(prof, "#718096")

        cat_cell = Paragraph(
            f"<b>{_normalize(cat)}</b>", styles["skill_cat"]
        )
        items_cell = Paragraph(_normalize(items_text), styles["body"])
        prof_cell = Paragraph(
            f'<font color="{prof_color}"><b>{prof}</b></font>',
            styles["body"],
        )

        table_data.append([cat_cell, items_cell, prof_cell])

    # 列宽
    col_widths = [CONTENT_WIDTH * 0.18, CONTENT_WIDTH * 0.67, CONTENT_WIDTH * 0.15]

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_BG, HexColor("#ffffff")]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, DIVIDER_COLOR),
        ("BOX", (0, 0), (-1, -1), 0.5, DIVIDER_COLOR),
    ]))

    story.append(table)
    return story


def _render_optimization_notes(notes, styles: dict) -> list:
    """渲染优化说明（仅 OptimizedResume 时使用）"""
    story = []

    story.append(Spacer(1, 10))
    story.append(Paragraph("简历优化说明", styles["section"]))
    story.append(_section_divider())

    # 改进摘要
    if notes.improvement_summary:
        story.append(Paragraph(
            f"<b>改进摘要:</b> {_normalize(notes.improvement_summary)}",
            styles["body"],
        ))

    # 评分对比
    score_row = (
        f"优化前评分: <b>{notes.overall_score_before}/10</b>"
        f"  →  优化后评分: <b>{notes.overall_score_after}/10</b>"
    )
    story.append(Paragraph(score_row, styles["body"]))

    # 植入关键词
    if notes.keywords_added:
        kw_text = "  ".join(
            f'<font color="#2b6cb0">#{k}</font>'
            for k in notes.keywords_added
        )
        story.append(Paragraph(f"植入关键词: {kw_text}", styles["highlight"]))

    # 量化改进
    if notes.quantified_improvements:
        story.append(Paragraph("<b>量化改进:</b>", styles["body"]))
        items = [
            ListItem(Paragraph(_normalize(q), styles["bullet"]),
                     value="circle", leftIndent=14)
            for q in notes.quantified_improvements
        ]
        story.append(ListFlowable(
            items, bulletType="bullet", bulletColor=ACCENT_COLOR,
            leftIndent=10, spaceAfter=4,
        ))

    # 各类优化明细
    if notes.optimization_types:
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>优化明细:</b>", styles["body"]))
        for opt in notes.optimization_types:
            story.append(Paragraph(
                f'<b>[{opt.category}]</b> {_normalize(opt.description)}',
                styles["opt_note"],
            ))
            if opt.before:
                story.append(Paragraph(
                    f'  优化前: {_normalize(opt.before)}',
                    styles["opt_note"],
                ))
            story.append(Paragraph(
                f'  优化后: {_normalize(opt.after)}',
                styles["opt_note"],
            ))

    # JD 对齐
    if notes.jd_alignments:
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>JD 对齐分析:</b>", styles["body"]))
        for align in notes.jd_alignments:
            strength_color = {
                "强匹配": "#38a169",
                "弱匹配": "#d69e2e",
                "无匹配": "#e53e3e",
            }.get(align.alignment_strength, "#718096")
            story.append(Paragraph(
                f'<font color="{strength_color}"><b>[{align.alignment_strength}]</b></font>'
                f' {_normalize(align.jd_requirement)} → {_normalize(align.resume_match)}',
                styles["opt_note"],
            ))

    # 真实性校验提醒
    if notes.authenticity_check:
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            '<font color="#e53e3e"><b>真实性校验提醒:</b></font>',
            styles["body"],
        ))
        for check in notes.authenticity_check:
            story.append(Paragraph(
                f"  {_normalize(check)}", styles["opt_note"],
            ))

    return story


# ──────────────────────────────────────────────
# 页脚回调
# ──────────────────────────────────────────────
def _on_page(canvas, doc):
    """页脚: 页码"""
    canvas.saveState()
    canvas.setFont(CJK_FONT_NAME, 8)
    canvas.setFillColor(MUTED_COLOR)
    page_num = canvas.getPageNumber()
    canvas.drawCentredString(
        PAGE_WIDTH / 2, BOTTOM_MARGIN / 2,
        f"第 {page_num} 页  |  面试作战指挥官生成",
    )
    canvas.restoreState()


# ──────────────────────────────────────────────
# 公开接口
# ──────────────────────────────────────────────
def generate_resume_pdf(
    resume: Union[ResumeDocument, OptimizedResume],
    include_optimization_notes: bool = True,
) -> bytes:
    """
    生成简历 PDF。

    参数:
        resume: ResumeDocument 或 OptimizedResume 实例
        include_optimization_notes: 如果是 OptimizedResume，是否包含优化说明

    返回:
        PDF 文件的 bytes 内容
    """
    font_name = _register_cjk_font()
    styles = _build_styles(font_name)

    # 判断输入类型
    if isinstance(resume, OptimizedResume):
        doc_data = resume.resume
        opt_notes = resume.optimization_notes if include_optimization_notes else None
    elif isinstance(resume, ResumeDocument):
        doc_data = resume
        opt_notes = None
    else:
        raise TypeError(f"不支持的类型: {type(resume)}")

    # 构建文档
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title=f"{doc_data.personal_info.name} - 简历",
        author="面试作战指挥官",
    )

    story = []

    # 1. 顶部: 姓名 + 联系方式
    story.extend(_render_header(doc_data.personal_info, styles))

    # 2. 个人总结
    story.extend(_render_summary(doc_data.summary, styles))

    # 3. 工作经历
    story.extend(_render_work_experiences(doc_data.work_experiences, styles))

    # 4. 项目经历
    story.extend(_render_project_experiences(doc_data.project_experiences, styles))

    # 5. 教育背景
    story.extend(_render_education(doc_data.education, styles))

    # 6. 专业技能
    story.extend(_render_skills(doc_data.skills, styles))

    # 7. 优化说明（如果有）
    if opt_notes:
        story.extend(_render_optimization_notes(opt_notes, styles))

    # 构建 PDF
    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)

    buffer.seek(0)
    return buffer.read()


def generate_resume_pdf_to_file(
    resume: Union[ResumeDocument, OptimizedResume],
    file_path: str,
    include_optimization_notes: bool = True,
) -> str:
    """
    生成简历 PDF 并保存到文件。

    返回: 文件路径
    """
    pdf_bytes = generate_resume_pdf(resume, include_optimization_notes)
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)
    return file_path


__all__ = [
    "generate_resume_pdf",
    "generate_resume_pdf_to_file",
]
