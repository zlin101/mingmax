import json

from app.llm.base import LLMClient
from app.llm.mock import DISCLAIMER, MOCK_BASIC_ANALYSIS, MOCK_FOLLOWUP_QUESTIONS, MockLLMClient


async def test_mock_llm_returns_basic_analysis_for_analysis_prompt() -> None:
    client = MockLLMClient()
    result = await client.generate(prompt="你是 mingmax 的紫微斗数语义分析助手...", context="ctx")
    parsed = json.loads(result)
    assert "summary" in parsed
    assert "strong_signals" in parsed
    assert isinstance(parsed["strong_signals"], list)


async def test_mock_llm_returns_theme_analysis_for_theme_prompt() -> None:
    client = MockLLMClient()
    result = await client.generate(prompt="你是 mingmax 的主题分析助手...", context="ctx")
    parsed = json.loads(result)
    assert "theme" in parsed
    assert "observations" in parsed


async def test_mock_llm_returns_followup_for_followup_prompt() -> None:
    client = MockLLMClient()
    result = await client.generate(prompt="你是 mingmax 的追问生成助手...", context="ctx")
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) > 0
    assert "question" in parsed[0]


async def test_mock_llm_returns_report_for_report_prompt() -> None:
    client = MockLLMClient()
    result = await client.generate(prompt="你是 mingmax 的 Markdown 报告生成助手...", context="ctx")
    assert "免责声明" in result
    assert isinstance(result, str)


async def test_mock_llm_is_llm_client() -> None:
    client = MockLLMClient()
    assert isinstance(client, LLMClient)


def test_disclaimer_constant_exists() -> None:
    assert "文化研究" in DISCLAIMER
    assert "不构成" in DISCLAIMER


def test_mock_basic_analysis_is_valid_json() -> None:
    parsed = json.loads(MOCK_BASIC_ANALYSIS)
    assert "summary" in parsed
    assert "strong_signals" in parsed


def test_mock_followup_questions_is_valid_json() -> None:
    parsed = json.loads(MOCK_FOLLOWUP_QUESTIONS)
    assert isinstance(parsed, list)
    for item in parsed:
        assert "question" in item
        assert "reason" in item
