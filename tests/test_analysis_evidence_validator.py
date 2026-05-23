import pytest

from app.agents.analysis_evidence_validator import validate_analysis_output
from app.llm.mock import DISCLAIMER
from app.schemas.analysis import AnalysisResult, FollowupQuestion, ThemeAnalysis


def _chart_facts(
    palaces: list[dict] | None = None,
    four_hua: dict | None = None,
) -> dict:
    palaces = palaces or [
        {"name": "命宫", "major_stars": ["紫微", "天府"], "mutagens": {"化禄": "紫微"}},
        {"name": "兄弟宫", "major_stars": ["天机"], "mutagens": {}},
        {"name": "夫妻宫", "major_stars": ["太阳"], "mutagens": {}},
        {"name": "子女宫", "major_stars": ["武曲"], "mutagens": {}},
        {"name": "财帛宫", "major_stars": ["天同"], "mutagens": {}},
        {"name": "疾厄宫", "major_stars": ["廉贞"], "mutagens": {}},
        {"name": "迁移宫", "major_stars": ["太阴"], "mutagens": {}},
        {"name": "交友宫", "major_stars": ["贪狼", "巨门"], "mutagens": {}},
        {"name": "官禄宫", "major_stars": [], "is_empty": True, "borrowed_from": {"major_stars": ["太阳"]}},
        {"name": "田宅宫", "major_stars": ["破军"], "mutagens": {}},
        {"name": "福德宫", "major_stars": [], "mutagens": {}},
        {"name": "父母宫", "major_stars": ["天梁"], "mutagens": {}},
    ]
    return {
        "ming_palace": "命宫",
        "body_palace": "夫妻宫",
        "four_hua": four_hua or {"hua_lu": "紫微", "hua_quan": "太阴", "hua_ke": "右弼", "hua_ji": "天机"},
        "palaces": palaces,
    }


def _analysis(**overrides) -> AnalysisResult:
    defaults = {
        "summary": "测试分析摘要",
        "strong_signals": ["命宫紫微化禄为较强信号"],
        "weak_hypotheses": ["迁移宫太阴可能暗示外在表现细腻"],
        "cross_checks": ["命宫与迁移宫构成对宫关系"],
        "safety_note": "仅供文化研究参考",
    }
    defaults.update(overrides)
    return AnalysisResult(**defaults)


def _theme(theme: str = "career", **overrides) -> ThemeAnalysis:
    defaults = {
        "theme": theme,
        "observations": ["命宫紫微化禄显示事业可能较强"],
        "supporting_evidence": ["命宫(index 0): 紫微化禄"],
        "uncertainty": "证据不足以支持强结论",
        "followup_questions": ["事业方向是否偏向管理？"],
    }
    defaults.update(overrides)
    return ThemeAnalysis(**defaults)


def _followup(question: str = "你的事业方向如何？", **overrides) -> FollowupQuestion:
    defaults = {"question": question, "reason": "验证命宫信号", "related_chart_factors": ["命宫"]}
    defaults.update(overrides)
    return FollowupQuestion(**defaults)


# --- valid output produces no issues ---


def test_valid_output_no_issues() -> None:
    facts = _chart_facts()
    analysis = _analysis()
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=f"# 报告\n{DISCLAIMER}",
    )
    assert len(issues) == 0


# --- fabricated star name ---


def test_fabricated_star_in_analysis() -> None:
    facts = _chart_facts()
    analysis = _analysis(strong_signals=["七杀坐命宫为较强信号"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_STAR"]
    assert len(fabricated) >= 1


def test_fabricated_star_in_theme() -> None:
    facts = _chart_facts()
    theme = _theme(observations=["天相坐命宫显示人际关系和谐"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=_analysis(),
        theme_analyses=[theme],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_STAR"]
    assert len(fabricated) >= 1


# --- fabricated palace name ---


def test_fabricated_palace_in_analysis() -> None:
    facts = _chart_facts(
        palaces=[
            {"name": "命宫", "major_stars": ["紫微"], "mutagens": {}},
            {"name": "兄弟宫", "major_stars": ["天机"], "mutagens": {}},
        ]
    )
    analysis = _analysis(weak_hypotheses=["父母宫主星暗示与长辈关系"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_PALACE"]
    assert len(fabricated) >= 1


# --- fabricated four_hua ---


def test_fabricated_hua_in_output() -> None:
    facts = _chart_facts()
    analysis = _analysis(strong_signals=["武曲化忌在子女宫为较强信号"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_MUTAGEN"]
    assert len(fabricated) >= 1


# --- absolute/threat language ---


ABSOLUTE_PHRASES = ["必然成功", "一定会离婚", "命中注定贫穷", "你绝对会遭遇重大疾病"]


@pytest.mark.parametrize("phrase", ABSOLUTE_PHRASES)
def test_absolute_language_in_analysis(phrase: str) -> None:
    facts = _chart_facts()
    analysis = _analysis(summary=phrase)
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    absolute = [i for i in issues if i.code == "UNSAFE_EXPRESSION"]
    assert len(absolute) >= 1


def test_absolute_language_in_theme() -> None:
    facts = _chart_facts()
    theme = _theme(observations=["你的婚姻注定失败"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=_analysis(),
        theme_analyses=[theme],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    absolute = [i for i in issues if i.code == "UNSAFE_EXPRESSION"]
    assert len(absolute) >= 1


def test_absolute_language_in_followup() -> None:
    facts = _chart_facts()
    fq = _followup(question="你一定会遇到事业危机吗？")
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=_analysis(),
        theme_analyses=[],
        followup_questions=[fq],
        report_markdown=DISCLAIMER,
    )
    absolute = [i for i in issues if i.code == "UNSAFE_EXPRESSION"]
    assert len(absolute) >= 1


# --- missing disclaimer ---


def test_missing_disclaimer_in_report() -> None:
    facts = _chart_facts()
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=_analysis(),
        theme_analyses=[],
        followup_questions=[],
        report_markdown="# 报告\n这是一个没有声明的报告",
    )
    disclaimer_issues = [i for i in issues if i.code == "MISSING_DISCLAIMER"]
    assert len(disclaimer_issues) >= 1


def test_null_report_no_disclaimer_issue() -> None:
    facts = _chart_facts()
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=_analysis(),
        theme_analyses=[],
        followup_questions=[],
        report_markdown=None,
    )
    disclaimer_issues = [i for i in issues if i.code == "MISSING_DISCLAIMER"]
    assert len(disclaimer_issues) == 0


# --- None fields handled gracefully ---


def test_validator_handles_none_safety_note() -> None:
    facts = _chart_facts()
    analysis = AnalysisResult(
        summary="测试",
        strong_signals=[],
        weak_hypotheses=[],
        cross_checks=[],
        safety_note=None,
    )
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    assert not any(i.code == "FABRICATED_STAR" and "None" in i.message for i in issues)


def test_validator_handles_none_uncertainty() -> None:
    facts = _chart_facts()
    theme = ThemeAnalysis(
        theme="career",
        observations=["命宫紫微化禄"],
        supporting_evidence=["命宫"],
        uncertainty=None,
        followup_questions=[],
    )
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=_analysis(),
        theme_analyses=[theme],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    crash_issues = [i for i in issues if "None" in i.message]
    assert len(crash_issues) == 0
