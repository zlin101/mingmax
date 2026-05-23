from __future__ import annotations

from pydantic import BaseModel

from app.schemas.analysis import AnalysisResult, FollowupQuestion, ThemeAnalysis


class ValidationIssue(BaseModel):
    severity: str  # "error" | "warning"
    code: str  # FABRICATED_STAR, FABRICATED_PALACE, FABRICATED_MUTAGEN, UNSAFE_EXPRESSION, MISSING_DISCLAIMER
    message: str
    context: str = ""


UNSAFE_PATTERNS = ["必然", "一定会", "命中注定", "绝对会", "注定", "不可避免", "肯定"]

_ALL_MAJOR_STARS = {
    "紫微",
    "天机",
    "太阳",
    "武曲",
    "天同",
    "廉贞",
    "天府",
    "太阴",
    "贪狼",
    "巨门",
    "天相",
    "天梁",
    "七杀",
    "破军",
}

_MUTAGEN_MAP = {"化禄": "hua_lu", "化权": "hua_quan", "化科": "hua_ke", "化忌": "hua_ji"}


def _collect_valid_names(chart_facts: dict) -> tuple[set[str], set[str], set[str]]:
    valid_stars: set[str] = set()
    valid_palaces: set[str] = set()
    valid_mutagens: set[str] = set()

    for p in chart_facts.get("palaces", []):
        name = p.get("name", "")
        if name:
            valid_palaces.add(name)
        for s in p.get("major_stars", []):
            valid_stars.add(s)
        for s in p.get("minor_stars", []):
            valid_stars.add(s)
        for s in p.get("adjective_stars", []):
            valid_stars.add(s)
        if p.get("borrowed_from") and "major_stars" in p["borrowed_from"]:
            for s in p["borrowed_from"]["major_stars"]:
                valid_stars.add(s)
        for label, star_name in p.get("mutagens", {}).items():
            valid_mutagens.add(f"{star_name}{label}")

    four_hua = chart_facts.get("four_hua", {})
    for field, star_name in four_hua.items():
        if star_name:
            for label, hf in _MUTAGEN_MAP.items():
                if hf == field:
                    valid_mutagens.add(f"{star_name}{label}")

    return valid_stars, valid_palaces, valid_mutagens


def _check_text_for_fabricated_stars(text: str, valid_stars: set[str]) -> list[ValidationIssue]:
    issues = []
    for star in _ALL_MAJOR_STARS:
        if star in text and star not in valid_stars:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="FABRICATED_STAR",
                    message=f"Star '{star}' referenced but not in chart_facts",
                    context=text[:200],
                )
            )
    return issues


def _check_text_for_fabricated_palaces(text: str, valid_palaces: set[str]) -> list[ValidationIssue]:
    _ALL_PALACE_NAMES = {
        "命宫",
        "兄弟宫",
        "夫妻宫",
        "子女宫",
        "财帛宫",
        "疾厄宫",
        "迁移宫",
        "交友宫",
        "官禄宫",
        "田宅宫",
        "福德宫",
        "父母宫",
    }
    issues = []
    for palace in _ALL_PALACE_NAMES:
        if palace in text and palace not in valid_palaces:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="FABRICATED_PALACE",
                    message=f"Palace '{palace}' referenced but not in chart_facts",
                    context=text[:200],
                )
            )
    return issues


def _check_text_for_fabricated_mutagens(text: str, valid_mutagens: set[str]) -> list[ValidationIssue]:
    issues = []
    for star in _ALL_MAJOR_STARS:
        for label in _MUTAGEN_MAP:
            pattern = f"{star}{label}"
            if pattern in text and pattern not in valid_mutagens:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="FABRICATED_MUTAGEN",
                        message=f"Mutagen '{pattern}' referenced but not in chart_facts",
                        context=text[:200],
                    )
                )
    return issues


def _check_text_for_unsafe_expressions(text: str) -> list[ValidationIssue]:
    issues = []
    for pattern in UNSAFE_PATTERNS:
        if pattern in text:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="UNSAFE_EXPRESSION",
                    message=f"Unsafe expression '{pattern}' found",
                    context=text[:200],
                )
            )
    return issues


def _check_all_text(
    texts: list[str], valid_stars: set[str], valid_palaces: set[str], valid_mutagens: set[str]
) -> list[ValidationIssue]:
    issues = []
    seen_stars: set[str] = set()
    seen_palaces: set[str] = set()
    seen_mutagens: set[str] = set()
    seen_unsafe: set[str] = set()

    for text in texts:
        for issue in _check_text_for_fabricated_stars(text, valid_stars):
            key = f"{issue.code}:{issue.message}"
            if key not in seen_stars:
                seen_stars.add(key)
                issues.append(issue)
        for issue in _check_text_for_fabricated_palaces(text, valid_palaces):
            key = f"{issue.code}:{issue.message}"
            if key not in seen_palaces:
                seen_palaces.add(key)
                issues.append(issue)
        for issue in _check_text_for_fabricated_mutagens(text, valid_mutagens):
            key = f"{issue.code}:{issue.message}"
            if key not in seen_mutagens:
                seen_mutagens.add(key)
                issues.append(issue)
        for issue in _check_text_for_unsafe_expressions(text):
            key = f"{issue.code}:{issue.message}"
            if key not in seen_unsafe:
                seen_unsafe.add(key)
                issues.append(issue)
    return issues


def validate_analysis_output(
    chart_facts: dict,
    analysis: AnalysisResult,
    theme_analyses: list[ThemeAnalysis],
    followup_questions: list[FollowupQuestion],
    report_markdown: str | None,
) -> list[ValidationIssue]:
    valid_stars, valid_palaces, valid_mutagens = _collect_valid_names(chart_facts)

    texts: list[str] = [
        analysis.summary,
        analysis.safety_note,
        *analysis.strong_signals,
        *analysis.weak_hypotheses,
        *analysis.cross_checks,
    ]

    for ta in theme_analyses:
        texts.extend([ta.theme, ta.uncertainty])
        texts.extend(ta.observations)
        texts.extend(ta.supporting_evidence)
        texts.extend(ta.followup_questions)

    for fq in followup_questions:
        texts.append(fq.question)
        texts.append(fq.reason)
        texts.extend(fq.related_chart_factors)

    issues = _check_all_text(texts, valid_stars, valid_palaces, valid_mutagens)

    if report_markdown is not None:
        report_issues = _check_all_text([report_markdown], valid_stars, valid_palaces, valid_mutagens)
        issues.extend(report_issues)

        if "免责声明" not in report_markdown and "文化研究" not in report_markdown:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="MISSING_DISCLAIMER",
                    message="Report does not contain disclaimer",
                )
            )

    return issues
