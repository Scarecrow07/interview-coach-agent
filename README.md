# 智能面试准备 Agent

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://scarecrow07-interview-coach-agent.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/Scarecrow07/interview-coach-agent)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

🎯 **面试作战指挥官** - 基于 LangChain + DeepSeek V4 的智能面试准备全流程助手

## 🚀 快速开始

### 在线体验
直接访问在线应用：[Streamlit Cloud](https://scarecrow07-interview-coach-agent.streamlit.app)

### 本地运行

```bash
# 克隆仓库
git clone https://github.com/Scarecrow07/interview-coach-agent.git
cd interview-coach-agent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填写 DEEPSEEK_API_KEY

# 启动应用
streamlit run api/streamlit_app.py
```

## 📋 功能特性

| 功能 | 描述 |
|------|------|
| 📝 **简历准备** | 上传简历或填写背景创建结构化简历 |
| ✨ **简历优化** | 针对JD优化简历，植入关键词，量化成果 |
| 📋 **JD分析** | 深度分析职位描述，提炼核心职责和隐藏信息 |
| 🔍 **简历分析** | 结合JD进行针对性分析，挖掘STAR-L成就 |
| 📊 **匹配度** | 量化评估候选人能力与JD的匹配程度 |
| 🎯 **面试方案** | 自我介绍、项目介绍、15题问答库 |
| 📝 **笔试题目** | 基于JD生成针对性笔试题 |
| 📚 **最终手册** | 整合所有报告，支持Markdown下载 |

## 🔧 技术特点

- ✅ 状态机驱动的流程编排
- ✅ 三层缓存机制（内存→Redis→SQLite）
- ✅ Pydantic结构化输出，格式一致
- ✅ 会话持久化，支持跨会话恢复
- ✅ 隐私保护，敏感信息脱敏
- ✅ 异步并行生成面试方案

## 📦 项目结构

```
interview_coach/
├── config/              # 配置管理
├── core/                # 核心模块（状态机、缓存、会话）
├── models/              # Pydantic结构化模型
├── services/            # 业务服务
├── api/                 # Streamlit Web应用
├── utils/               # 工具函数
├── docs/                # GitHub Pages
├── .streamlit/          # Streamlit配置
├── packages.txt         # Streamlit Cloud依赖
├── requirements.txt     # 本地依赖
└── README.md
```

## 🌐 部署方式

### Streamlit Cloud（推荐）
1. Fork本仓库
2. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
3. 连接GitHub账号，选择仓库
4. 设置环境变量 `DEEPSEEK_API_KEY`
5. 自动部署完成

### GitHub Pages
项目介绍页面：[https://scarecrow07.github.io/interview-coach-agent](https://scarecrow07.github.io/interview-coach-agent)

## ⚙️ 配置

必需配置：
```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat
```

可选配置：
```env
REDIS_URL=redis://localhost:6379  # Redis缓存
LOG_LEVEL=INFO
```

## 📊 使用流程

```
简历准备 → JD分析 → 简历分析 → 匹配度 → 面试方案 → 最终手册
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License