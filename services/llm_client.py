from langchain_openai import ChatOpenAI

from config.settings import settings


def get_llm() -> ChatOpenAI:
    """获取LLM实例"""
    return ChatOpenAI(
        model=settings.DEEPSEEK_MODEL,
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
        temperature=0.3,
    )


# 全局LLM实例
llm = get_llm()