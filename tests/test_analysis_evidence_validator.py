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


def _chart_facts_with_evidence() -> dict:
    """chart_facts with a realistic evidence_index for evidence ID tests."""
    facts = _chart_facts(
        palaces=[
            {"name": "命宫", "major_stars": ["紫微", "天府"], "mutagens": {"化禄": "紫微"}},
            {"name": "兄弟宫", "major_stars": ["天机"], "mutagens": {}},
        ]
    )
    facts["evidence_index"] = [
        {"id": "palace:0", "type": "palace", "label": "命宫(index 0)"},
        {"id": "palace:1", "type": "palace", "label": "兄弟宫(index 1)"},
        {"id": "star:0:紫微", "type": "star", "label": "紫微在命宫"},
        {"id": "star:0:天府", "type": "star", "label": "天府在命宫"},
        {"id": "star:1:天机", "type": "star", "label": "天机在兄弟宫"},
        {"id": "mutagen:0:hua_lu:紫微", "type": "mutagen", "label": "紫微化禄在命宫"},
        {"id": "relation:0:opposite:6", "type": "relation", "label": "命宫对宫迁移宫"},
        {"id": "relation:0:sfsz:0,4,6,8", "type": "relation", "label": "命宫三方四正"},
        {"id": "borrowed:2:from:6:太阳", "type": "borrowed", "label": "官禄宫(空宫)借太阳"},
    ]
    return facts


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


# --- Enhanced validator: evidence_id, palace-star binding, mutagen binding, unsupported time layer ---


def test_fabricated_evidence_id_star() -> None:
    """star:5:贪狼 does not exist in evidence_index."""
    facts = _chart_facts_with_evidence()
    analysis = _analysis(strong_signals=["依据 star:5:贪狼（证据不存在）"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) >= 1


def test_fabricated_evidence_id_palace() -> None:
    """palace:99 does not exist in evidence_index."""
    facts = _chart_facts_with_evidence()
    analysis = _analysis(strong_signals=["依据 palace:99 观察到"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) >= 1


def test_fabricated_evidence_id_mutagen() -> None:
    """mutagen:0:hua_ji:贪狼 does not exist."""
    facts = _chart_facts_with_evidence()
    analysis = _analysis(strong_signals=["mutagen:0:hua_ji:贪狼 不存在"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) >= 1


def test_fabricated_evidence_id_relation() -> None:
    """relation:0:opposite:99 does not exist."""
    facts = _chart_facts_with_evidence()
    analysis = _analysis(strong_signals=["relation:0:opposite:99 不存在"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) >= 1


def test_fabricated_evidence_id_borrowed() -> None:
    """borrowed:99:from:0:紫微 does not exist."""
    facts = _chart_facts_with_evidence()
    analysis = _analysis(strong_signals=["borrowed:99:from:0:紫微 不存在"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) >= 1


def test_valid_evidence_id_palace_not_flagged() -> None:
    """palace:0 exists in evidence_index and should not be flagged."""
    facts = _chart_facts_with_evidence()
    analysis = _analysis(strong_signals=["依据 palace:0 观察到"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) == 0


def test_valid_evidence_id_star_not_flagged() -> None:
    """star:0:紫微 exists in evidence_index and should not be flagged."""
    facts = _chart_facts_with_evidence()
    analysis = _analysis(strong_signals=["依据 star:0:紫微 观察到"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) == 0


def test_valid_evidence_id_mutagen_not_flagged() -> None:
    """mutagen:0:hua_lu:紫微 exists in evidence_index."""
    facts = _chart_facts_with_evidence()
    analysis = _analysis(strong_signals=["依据 mutagen:0:hua_lu:紫微 观察到"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) == 0


def test_valid_minor_star_evidence_id_not_flagged() -> None:
    """minor star evidence ID should not be flagged as fabricated."""
    from app.engines.chart_facts import build_chart_facts
    from app.schemas.chart import NormalizedChart, Palace, Star

    chart = NormalizedChart(
        chart_id="test",
        source="test",
        summary="test",
        palaces=[
            Palace(
                index=0,
                name="命宫",
                stars=[
                    Star(name="左辅", brightness="旺", category="minor"),
                ],
                opposite_palace_index=6,
                san_fang_si_zheng_indexes=[0, 4, 6, 8],
                is_empty=False,
            ),
        ],
        ming_palace_index=0,
    )
    chart_facts = build_chart_facts(chart)

    analysis = _analysis(strong_signals=["依据 star:0:左辅 观察到"])
    issues = validate_analysis_output(
        chart_facts=chart_facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) == 0


def test_valid_adjective_star_evidence_id_not_flagged() -> None:
    """adjective star evidence ID should not be flagged as fabricated."""
    from app.engines.chart_facts import build_chart_facts
    from app.schemas.chart import NormalizedChart, Palace, Star

    chart = NormalizedChart(
        chart_id="test",
        source="test",
        summary="test",
        palaces=[
            Palace(
                index=0,
                name="命宫",
                stars=[
                    Star(name="天魁", brightness="得", category="adjective"),
                ],
                opposite_palace_index=6,
                san_fang_si_zheng_indexes=[0, 4, 6, 8],
                is_empty=False,
            ),
        ],
        ming_palace_index=0,
    )
    chart_facts = build_chart_facts(chart)

    analysis = _analysis(strong_signals=["依据 star:0:天魁 观察到"])
    issues = validate_analysis_output(
        chart_facts=chart_facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) == 0


def test_invalid_star_palace_binding() -> None:
    """天机 is in the chart (兄弟宫) but NOT in 夫妻宫."""
    facts = _chart_facts(
        palaces=[
            {"name": "命宫", "major_stars": ["紫微"], "mutagens": {}},
            {"name": "兄弟宫", "major_stars": ["天机"], "mutagens": {}},
            {"name": "夫妻宫", "major_stars": ["太阳"], "mutagens": {}},
        ]
    )
    analysis = _analysis(strong_signals=["天机在夫妻宫为较强信号"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    binding = [i for i in issues if i.code == "INVALID_STAR_PALACE_BINDING"]
    assert len(binding) >= 1


def test_valid_star_palace_binding_not_flagged() -> None:
    facts = _chart_facts(
        palaces=[
            {"name": "命宫", "major_stars": ["紫微"], "mutagens": {}},
        ]
    )
    analysis = _analysis(strong_signals=["紫微在命宫为较强信号"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    binding = [i for i in issues if i.code == "INVALID_STAR_PALACE_BINDING"]
    assert len(binding) == 0


def test_invalid_mutagen_palace_binding() -> None:
    """天机 has 化忌 at chart level but NOT in 命宫."""
    facts = _chart_facts(
        palaces=[
            {"name": "命宫", "major_stars": ["紫微"], "mutagens": {}},
            {"name": "夫妻宫", "major_stars": ["天机"], "mutagens": {"化忌": "天机"}},
        ]
    )
    analysis = _analysis(weak_hypotheses=["命宫天机化忌可能暗示压力"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    binding = [i for i in issues if i.code == "INVALID_MUTAGEN_PALACE_BINDING"]
    assert len(binding) >= 1


def test_unsupported_time_layer_reference() -> None:
    facts = _chart_facts()
    analysis = _analysis(strong_signals=["流年显示事业压力"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    unsupported = [i for i in issues if i.code == "UNSUPPORTED_TIME_LAYER"]
    assert len(unsupported) >= 1


@pytest.mark.parametrize("term", ["流年", "流月", "流日", "流时"])
def test_unsupported_time_layer_variants(term: str) -> None:
    facts = _chart_facts()
    analysis = _analysis(summary=f"{term}运行趋势分析")
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    unsupported = [i for i in issues if i.code == "UNSUPPORTED_TIME_LAYER"]
    assert len(unsupported) >= 1


# --- decadal and metadata evidence ID tests ---


def test_valid_decadal_evidence_id_not_flagged() -> None:
    """decadal:0:10-19 exists in evidence_index and should not be flagged."""
    from app.engines.chart_facts import build_chart_facts
    from app.schemas.chart import DecadalRange, NormalizedChart, Palace

    chart = NormalizedChart(
        chart_id="test",
        source="test",
        summary="test",
        palaces=[
            Palace(
                index=0,
                name="命宫",
                stars=[],
                opposite_palace_index=6,
                san_fang_si_zheng_indexes=[0, 4, 6, 8],
                is_empty=False,
                decadal=DecadalRange(
                    start_age=10,
                    end_age=19,
                    heavenly_stem="甲",
                    earthly_branch="子",
                    palace_index=0,
                    palace_name="命宫",
                ),
            ),
        ],
        ming_palace_index=0,
    )
    chart_facts = build_chart_facts(chart)

    analysis = _analysis(strong_signals=["依据 decadal:0:10-19 观察到"])
    issues = validate_analysis_output(
        chart_facts=chart_facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) == 0


def test_fabricated_decadal_evidence_id() -> None:
    """decadal:99:99-109 does not exist in evidence_index."""
    from app.engines.chart_facts import build_chart_facts
    from app.schemas.chart import DecadalRange, NormalizedChart, Palace

    chart = NormalizedChart(
        chart_id="test",
        source="test",
        summary="test",
        palaces=[
            Palace(
                index=0,
                name="命宫",
                stars=[],
                opposite_palace_index=6,
                san_fang_si_zheng_indexes=[0, 4, 6, 8],
                is_empty=False,
                decadal=DecadalRange(
                    start_age=10,
                    end_age=19,
                    heavenly_stem="甲",
                    earthly_branch="子",
                    palace_index=0,
                    palace_name="命宫",
                ),
            ),
        ],
        ming_palace_index=0,
    )
    chart_facts = build_chart_facts(chart)

    analysis = _analysis(strong_signals=["依据 decadal:99:99-109 观察到"])
    issues = validate_analysis_output(
        chart_facts=chart_facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) >= 1


def test_valid_metadata_evidence_id_not_flagged() -> None:
    """metadata:lunar_date exists in evidence_index and should not be flagged."""
    from app.engines.chart_facts import build_chart_facts
    from app.schemas.chart import ChartMetadata, NormalizedChart, Palace

    chart = NormalizedChart(
        chart_id="test",
        source="test",
        summary="test",
        palaces=[
            Palace(
                index=0,
                name="命宫",
                stars=[],
                opposite_palace_index=6,
                san_fang_si_zheng_indexes=[0, 4, 6, 8],
                is_empty=False,
            ),
        ],
        ming_palace_index=0,
        metadata=ChartMetadata(lunar_date="二零二六年四月十八日"),
    )
    chart_facts = build_chart_facts(chart)

    analysis = _analysis(strong_signals=["依据 metadata:lunar_date 观察到"])
    issues = validate_analysis_output(
        chart_facts=chart_facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) == 0


def test_fabricated_metadata_evidence_id() -> None:
    """metadata:nonexistent_field does not exist in evidence_index."""
    from app.engines.chart_facts import build_chart_facts
    from app.schemas.chart import ChartMetadata, NormalizedChart, Palace

    chart = NormalizedChart(
        chart_id="test",
        source="test",
        summary="test",
        palaces=[
            Palace(
                index=0,
                name="命宫",
                stars=[],
                opposite_palace_index=6,
                san_fang_si_zheng_indexes=[0, 4, 6, 8],
                is_empty=False,
            ),
        ],
        ming_palace_index=0,
        metadata=ChartMetadata(lunar_date="二零二六年四月十八日"),
    )
    chart_facts = build_chart_facts(chart)

    analysis = _analysis(strong_signals=["依据 metadata:nonexistent_field 观察到"])
    issues = validate_analysis_output(
        chart_facts=chart_facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    fabricated = [i for i in issues if i.code == "FABRICATED_EVIDENCE_ID"]
    assert len(fabricated) >= 1


def test_supported_decadal_term_not_flagged() -> None:
    """大限 is now supported and should not trigger UNSUPPORTED_TIME_LAYER."""
    facts = _chart_facts()
    analysis = _analysis(strong_signals=["大限显示事业发展趋势"])
    issues = validate_analysis_output(
        chart_facts=facts,
        analysis=analysis,
        theme_analyses=[],
        followup_questions=[],
        report_markdown=DISCLAIMER,
    )
    unsupported = [i for i in issues if i.code == "UNSUPPORTED_TIME_LAYER"]
    assert len(unsupported) == 0
