from app.llm.base import LLMClient

DISCLAIMER = "本分析仅供文化研究、娱乐体验与自我反思参考，不构成医学、法律、财务、心理诊断或人生决策依据。"

MOCK_ANALYSIS = """# 紫微斗数分析报告

## 免责声明

本分析仅供文化研究、娱乐体验与自我反思参考，不构成医学、法律、财务、心理诊断或人生决策依据。

## 命盘结构摘要

这是一份基于 stub 排盘的模拟分析，用于验证系统闭环。

## 主要观察

当前命盘为 stub 数据，不包含真实星曜分布。
"""


class MockLLMClient(LLMClient):
    async def generate(self, prompt: str, context: str = "") -> str:
        return MOCK_ANALYSIS
