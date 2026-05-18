import pytest

from app.agents.prompt_loader import PromptLoadError, load_prompt


def test_load_prompt_exists() -> None:
    for name in ("ziwei_analysis", "theme_analysis", "followup_questions", "report"):
        content = load_prompt(name)
        assert len(content) > 0


def test_load_prompt_not_found() -> None:
    with pytest.raises(PromptLoadError, match="Prompt file not found"):
        load_prompt("nonexistent_prompt")


def test_ziwei_analysis_prompt_safety() -> None:
    content = load_prompt("ziwei_analysis")
    assert "不得" in content
    assert "绝对化" in content


def test_report_prompt_contains_disclaimer_requirement() -> None:
    content = load_prompt("report")
    assert "免责声明" in content
    assert "不构成" in content
