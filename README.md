# 智能面试准备 Agent

基于 LangChain + DeepSeek V4 的多轮对话式面试准备助手，提供完整的面试准备全流程服务。

## 功能特性

### 核心功能
- 📝 **简历准备**：上传简历或填写背景创建结构化简历
- ✨ **简历优化**：针对性优化简历，植入关键词，量化成果
- 📋 **JD 分析**：深度分析职位描述，提炼核心职责和隐藏信息
- 🔍 **简历分析**：结合 JD 进行针对性分析，挖掘 STAR-L 成就
- 📊 **匹配度分析**：量化评估候选人能力与 JD 的匹配程度
- 🎯 **面试方案生成**：自我介绍、项目介绍、15题问答库
- 📝 **笔试题目生成**：基于 JD 生成针对性笔试题

### 技术特点
- 状态机驱动的流程编排
- 三层缓存机制（内存→Redis→SQLite）
- Pydantic 结构化输出，格式一致
- 会话持久化，支持跨会话恢复
- 隐私保护，敏感信息脱敏
- 异步并行生成面试方案

## 安装

```bash
# 克隆仓库
git clone https://github.com/Scarecrow07/interview-coach-agent.git
cd interview-coach-agent

# 安装依赖
pip install -r requirements.txt
```

## 配置

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必需配置：

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

REDIS_URL=redis://localhost:6379  # 可选
```

## 运行

### 启动 Web 应用

```bash
streamlit run api/streamlit_app.py
```

应用将在浏览器中打开，地址：`http://localhost:8501`

### 命令行模式

```bash
python main.py
```

## 使用指南

### 完整流程

1. **简历准备** - 选择上传已有简历或填写背景创建新简历
2. **JD 分析** - 输入目标职位 JD，获取深度分析报告
3. **简历分析** - 结合 JD 进行针对性简历分析
4. **匹配度分析** - 量化评估与 JD 的匹配程度
5. **面试方案生成** - 获取定制化自我介绍、项目介绍和问答库
6. **笔试题目** - 可选生成针对性笔试题
7. **最终手册** - 整合所有报告生成完整面试作战手册

### 输出内容

每个步骤生成结构化报告：

- **JD 分析报告**：岗位画像、核心职责、硬性要求、隐藏信息、高频问题预测
- **简历分析报告**：简历摘要、STAR-L 成就事件、核心优势、风险识别
- **匹配度报告**：整体匹配度评分、能力匹配明细、差距弥补方案
- **面试方案**：自我介绍、项目介绍、15题问答库（含完整回答示例）
- **最终手册**：整合所有报告，可直接打印使用

## 项目结构

```
interview_coach/
├── config/              # 配置管理
│   ├── settings.py      # Pydantic 配置
│   └── logging_config.py # 日志配置
│
├── core/                # 核心模块
│   ├── state_machine.py # 状态定义与流转
│   ├── session_manager.py # 持久化会话管理
│   ├── cache_manager.py # 三层缓存
│   ├── error_handler.py # 错误处理与降级
│   ├── privacy_protector.py # 隐私保护
│   └── flow_controller.py # 流程编排控制器
│
├── models/              # Pydantic 结构化模型
│   ├── resume_schema.py # 简历模型
│   ├── jd_schema.py     # JD 分析模型
│   ├── match_schema.py  # 匹配度模型
│   └── qa_schema.py     # 问答库模型
│
├── services/            # 业务服务
│   ├── llm_client.py    # LLM 客户端
│   ├── prompts.py       # Prompt 模板集合
│   ├── resume_service.py # 简历服务
│   ├── jd_service.py    # JD 分析服务
│   ├── resume_analysis_service.py # 简历分析服务
│   ├── match_service.py # 匹配度分析服务
│   └ interview_service.py # 面试方案生成服务
│
├── api/                 # API 层
│   └ streamlit_app.py   # Streamlit Web 应用
│
├── utils/               # 工具函数
│   └ metrics_collector.py # 指标收集
│
├── main.py              # 主入口
├── requirements.txt     # 依赖
├── .env.example         # 环境变量示例
└── README.md            # 项目说明
```

## 技术栈

- **Python 3.10+**
- **LangChain 0.3.0** - LLM 框架
- **DeepSeek V4** - 大语言模型
- **Streamlit** - Web 界面
- **Pydantic** - 数据验证
- **Redis** - 可选缓存层
- **SQLite** - 会话和缓存持久化

## 许可证

MIT License