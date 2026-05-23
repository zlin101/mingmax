import pytest

from app.agents.prompt_loader import PromptLoadError, load_prompt


def test_load_prompt_exists() -> None:
    for name in ("ziwei_analysis", "theme_analysis", "followup_questions", "report"):
        content = load_prompt(name)
        assert len(content) > 0


def test_load_prompt_not_found() -> None:
    with pytest.raises(PromptLoadError, match="Prompt file not found"):
        load_prompt("nonexistent_prompt")


def test_ziwei_analysis_prompt_requires_json() -> None:
    content = load_prompt("ziwei_analysis")
    assert "JSON" in content
    assert "不要输出 Markdown" in content or "不要使用代码块" in content
    assert "不得" in content
    assert "绝对化" in content


def test_theme_analysis_prompt_requires_json() -> None:
    content = load_prompt("theme_analysis")
    assert "JSON" in content
    assert "不要输出 Markdown" in content or "不要使用代码块" in content


def test_followup_questions_prompt_requires_json_array() -> None:
    content = load_prompt("followup_questions")
    assert "JSON" in content
    assert "不要输出 Markdown" in content or "不要使用代码块" in content


def test_report_prompt_contains_disclaimer_requirement() -> None:
    content = load_prompt("report")
    assert "免责声明" in content
    assert "不构成" in content


@pytest.mark.parametrize(
    "prompt_name",
    ["ziwei_analysis", "theme_analysis", "followup_questions", "report"],
)
def test_prompts_reference_chart_facts(prompt_name: str) -> None:
    content = load_prompt(prompt_name)
    assert "chart_facts" in content


@pytest.mark.parametrize(
    "prompt_name",
    ["ziwei_analysis", "theme_analysis", "followup_questions", "report"],
)
def test_prompts_prohibit_fabrication(prompt_name: str) -> None:
    content = load_prompt(prompt_name)
    assert "虚构" in content or "不存在" in content


def test_ziwei_analysis_prompt_requires_evidence_grounding() -> None:
    content = load_prompt("ziwei_analysis")
    assert "证据不足" in content or "不足以" in content
