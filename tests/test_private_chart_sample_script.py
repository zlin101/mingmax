from app.engines.chart_diff import ChartDiffResult, PalaceDiff
from scripts.verify_private_chart_sample import _count_mismatched_palaces, _parse_reference


def test_parse_reference_extracts_multibracket_four_hua_markers() -> None:
    text = """
├基本信息
│ ├性别 : 女
│ ├地理经度 : 121.500
│ ├钟表时间 : 2001-02-03 04:05
│ └身宫:午
├命盘十二宫
│ ├命  宫[甲子]
│ │ ├主星 : 紫微[庙][生年禄],天机[旺][生年忌]
│ │
│ ├兄弟宫[乙丑]
│ │ ├主星 : 太阴[旺][生年权]
│ │
│ └夫妻宫[丙寅][身宫]
│   ├主星 : 文昌[庙][生年科]
"""

    parsed = _parse_reference(text)

    assert parsed["gender"] == "female"
    assert parsed["clock_time"] == "2001-02-03T04:05"
    assert parsed["longitude"] == 121.5
    assert parsed["hua_lu"] == "紫微"
    assert parsed["hua_quan"] == "太阴"
    assert parsed["hua_ke"] == "文昌"
    assert parsed["hua_ji"] == "天机"


def test_count_mismatched_palaces_counts_unique_palace_indexes() -> None:
    result = ChartDiffResult(
        diffs=[
            PalaceDiff(
                palace_index=0,
                palace_name="命宫",
                field="major_stars",
                expected="A",
                actual="B",
                severity="error",
            ),
            PalaceDiff(
                palace_index=0,
                palace_name="命宫",
                field="is_body_palace",
                expected="True",
                actual="False",
                severity="warning",
            ),
            PalaceDiff(
                palace_index=-1,
                palace_name="",
                field="hua_lu",
                expected="A",
                actual="B",
                severity="error",
            ),
        ]
    )

    assert _count_mismatched_palaces(result) == 1
