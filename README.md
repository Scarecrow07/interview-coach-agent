# 智能面试准备 Agent

基于 LangChain + DeepSeek V4 的多轮对话式面试准备助手。

## 功能

- 简历准备（上传或创建）
- 简历优化
- JD 分析
- 简历分析
- 匹配度分析
- 面试方案生成
- 笔试题目生成

## 安装

```bash
pip install -r requirements.txt
```

## 配置

复制 `.env.example` 到 `.env` 并填写配置:

```bash
cp .env.example .env
```

必需配置:
- `DEEPSEEK_API_KEY`: DeepSeek API Key

## 运行

### 命令行模式

```bash
python main.py
```

### Web界面

```bash
streamlit run api/streamlit_app.py
```

## 项目结构

```
interview_coach/
├── config/          # 配置管理
├── core/            # 核心模块（状态机、缓存、会话）
├── models/          # Pydantic 结构化模型
├── services/        # 业务服务
├── api/             # API 和 UI
├── utils/           # 工具函数
├── tests/           # 测试
├── main.py          # 主入口
└── requirements.txt
```

## 技术栈

- Python 3.10+
- LangChain 0.3.0
- DeepSeek V4
- Streamlit
- Redis（可选）
- SQLite