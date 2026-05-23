import json

from app.llm.base import LLMClient

DISCLAIMER = "本分析仅供文化研究、娱乐体验与自我反思参考，不构成医学、法律、财务、心理诊断或人生决策依据。"

MOCK_BASIC_ANALYSIS = json.dumps(
    {
        "summary": "基于当前结构化命盘的总体观察。当前为 MockLLMClient 返回的模拟分析结果。",
        "strong_signals": ["命宫主星组合形成基本格局"],
        "weak_hypotheses": ["部分辅星影响需结合实际生活经验确认"],
        "cross_checks": ["命宫与迁移宫对宫关系"],
        "safety_note": DISCLAIMER,
    },
    ensure_ascii=False,
)

MOCK_THEME_ANALYSIS_TEMPLATE = json.dumps(
    {
        "theme": "{theme}",
        "observations": ["基于当前命盘结构的观察点"],
        "supporting_evidence": ["相关宫位与星曜依据"],
        "uncertainty": "当前为模拟分析，实际分析需结合完整命盘结构。",
        "followup_questions": ["可以进一步确认生活经验方向"],
    },
    ensure_ascii=False,
)

MOCK_FOLLOWUP_QUESTIONS = json.dumps(
    [
        {
            "question": "您是否注意到某些生活领域与当前命盘结构存在共鸣？",
            "reason": "帮助确认命盘结构与实际生活经验的对应关系",
            "related_chart_factors": ["命宫主星", "对宫关系"],
        }
    ],
    ensure_ascii=False,
)

MOCK_REPORT = f"""# 紫微斗数分析报告

## 免责声明

{DISCLAIMER}

## 命盘结构摘要

基于当前结构化命盘的分析概览。当前为 MockLLMClient 返回的模拟报告内容。

## 主要观察

基于命盘主星组合的基本格局观察。

## 主题分析

模拟主题分析结果。

## 宫位交叉验证

模拟交叉验证结果。

## 待确认问题

模拟待确认问题。

## 不确定性说明

当前为模拟分析，实际分析需结合完整命盘结构与用户生活经验。

## 自我反思建议

模拟自我反思建议。"""


class MockLLMClient(LLMClient):
    async def generate(self, prompt: str, context: str = "") -> str:
        if "追问生成" in prompt:
            return MOCK_FOLLOWUP_QUESTIONS
        if "主题分析助手" in prompt:
            actual_theme = "mock_theme"
            for line in prompt.split("\n"):
                if line.startswith("分析主题："):
                    actual_theme = line.removeprefix("分析主题：").strip()
                    break
            return MOCK_THEME_ANALYSIS_TEMPLATE.replace("{theme}", actual_theme)
        if "报告生成助手" in prompt:
            return MOCK_REPORT
        return MOCK_BASIC_ANALYSIS
