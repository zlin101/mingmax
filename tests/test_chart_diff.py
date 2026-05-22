from app.engines.chart_diff import (
    ChartDiffResult,
    ExpectedChartSnapshot,
    ExpectedPalaceSnapshot,
    PalaceDiff,
    diff_charts,
)
from app.schemas.chart import FourHua, NormalizedChart, Palace, Star


def _palace(
    index: int,
    name: str,
    major_stars: list[str] | None = None,
    is_body: bool = False,
    stem: str | None = "甲",
    branch: str | None = "子",
) -> Palace:
    stars = []
    for s in major_stars or []:
        stars.append(Star(name=s, brightness=None, category="major"))
    return Palace(
        index=index,
        name=name,
        heavenly_stem=stem,
        earthly_branch=branch,
        stars=stars,
        is_body_palace=is_body,
    )


def _chart(palaces: list[Palace], four_hua: FourHua | None = None) -> NormalizedChart:
    return NormalizedChart(
        chart_id="test-chart",
        source="test",
        summary="test chart",
        palaces=palaces,
        four_hua=four_hua,
    )


def _snapshot(
    palaces: list[ExpectedPalaceSnapshot] | None = None,
    hua_lu: str | None = None,
    hua_quan: str | None = None,
    hua_ke: str | None = None,
    hua_ji: str | None = None,
    palace_count: int | None = None,
) -> ExpectedChartSnapshot:
    p = palaces or []
    return ExpectedChartSnapshot(
        palace_count=palace_count if palace_count is not None else len(p),
        palaces=p,
        hua_lu=hua_lu,
        hua_quan=hua_quan,
        hua_ke=hua_ke,
        hua_ji=hua_ji,
    )


# --- Identical charts return empty diff ---


def test_diff_identical_charts() -> None:
    palaces = [
        _palace(0, "命宫", major_stars=["紫微"]),
        _palace(1, "兄弟宫", major_stars=["天机"]),
    ]
    snapshot = _snapshot(
        palaces=[
            ExpectedPalaceSnapshot(index=0, name="命宫", major_stars=["紫微"]),
            ExpectedPalaceSnapshot(index=1, name="兄弟宫", major_stars=["天机"]),
        ]
    )
    result = diff_charts(_chart(palaces), snapshot)
    assert result.is_match
    assert len(result.diffs) == 0


# --- Major star mismatch is error ---


def test_diff_major_star_mismatch() -> None:
    palaces = [
        _palace(0, "命宫", major_stars=["紫微"]),
    ]
    snapshot = _snapshot(
        palaces=[
            ExpectedPalaceSnapshot(index=0, name="命宫", major_stars=["天机"]),
        ]
    )
    result = diff_charts(_chart(palaces), snapshot)
    assert not result.is_match
    assert len(result.errors) == 1
    assert result.errors[0].field == "major_stars"
    assert result.errors[0].severity == "error"


# --- Optional field missing is warning ---


def test_diff_body_palace_missing_is_warning() -> None:
    palaces = [
        _palace(0, "夫妻宫", major_stars=["天府"], is_body=False),
    ]
    snapshot = _snapshot(
        palaces=[
            ExpectedPalaceSnapshot(index=0, name="夫妻宫", major_stars=["天府"], is_body_palace=True),
        ]
    )
    result = diff_charts(_chart(palaces), snapshot)
    assert result.is_match
    assert len(result.warnings) == 1
    assert result.warnings[0].field == "is_body_palace"
    assert result.warnings[0].severity == "warning"


# --- Palace count mismatch is error ---


def test_diff_palace_count_mismatch() -> None:
    palaces = [_palace(0, "命宫", major_stars=["紫微"])]
    snapshot = _snapshot(
        palaces=[ExpectedPalaceSnapshot(index=0, name="命宫", major_stars=["紫微"])],
    )
    snapshot.palace_count = 12
    result = diff_charts(_chart(palaces), snapshot)
    assert not result.is_match
    assert len(result.errors) == 1
    assert result.errors[0].field == "palace_count"


# --- Four hua mismatch is error ---


def test_diff_four_hua_mismatch() -> None:
    palaces = [_palace(0, "命宫")]
    four_hua = FourHua(hua_lu="贪狼", hua_ji="天机")
    snapshot = _snapshot(
        palaces=[ExpectedPalaceSnapshot(index=0, name="命宫")],
        hua_lu="太阳",
        hua_ji="天机",
    )
    result = diff_charts(_chart(palaces, four_hua=four_hua), snapshot)
    assert not result.is_match
    assert len(result.errors) == 1
    assert result.errors[0].field == "hua_lu"


def test_diff_four_hua_match() -> None:
    palaces = [_palace(0, "命宫")]
    four_hua = FourHua(hua_lu="贪狼", hua_quan="太阴", hua_ke="右弼", hua_ji="天机")
    snapshot = _snapshot(
        palaces=[ExpectedPalaceSnapshot(index=0, name="命宫")],
        hua_lu="贪狼",
        hua_quan="太阴",
        hua_ke="右弼",
        hua_ji="天机",
    )
    result = diff_charts(_chart(palaces, four_hua=four_hua), snapshot)
    assert result.is_match


# --- Missing palace is error ---


def test_diff_missing_palace() -> None:
    palaces = [_palace(0, "命宫"), _palace(1, "兄弟宫")]
    snapshot = _snapshot(
        palaces=[
            ExpectedPalaceSnapshot(index=0, name="命宫"),
            ExpectedPalaceSnapshot(index=1, name="兄弟宫"),
            ExpectedPalaceSnapshot(index=2, name="夫妻宫"),
        ],
    )
    result = diff_charts(_chart(palaces), snapshot)
    assert not result.is_match
    palace_diffs = [d for d in result.errors if d.field == "name"]
    assert len(palace_diffs) == 1


# --- Index mismatch is error ---


def test_diff_palace_index_mismatch_is_warning() -> None:
    palaces = [_palace(1, "命宫")]
    snapshot = _snapshot(
        palaces=[ExpectedPalaceSnapshot(index=0, name="命宫")],
    )
    result = diff_charts(_chart(palaces), snapshot)
    assert result.is_match
    assert any(d.field == "index" for d in result.warnings)


# --- Diff output contains no private data ---


def test_diff_output_no_private_data() -> None:
    result = ChartDiffResult(
        diffs=[
            PalaceDiff(
                palace_index=0,
                palace_name="命宫",
                field="major_stars",
                expected="['紫微']",
                actual="['天机']",
                severity="error",
            )
        ]
    )
    output = result.model_dump_json()
    assert "1998" not in output
    assert "出生" not in output
    assert "经度" not in output
