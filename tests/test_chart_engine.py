from datetime import datetime, timedelta, timezone

import pytest

from app.engines.chart_normalizer import ChartNormalizer
from app.engines.ziwei_chart_engine import UnsupportedCalendarTypeError, ZiweiChartEngine
from app.schemas.birth import BirthInfo, Gender


def _birth_info(
    year: int = 1995,
    month: int = 5,
    day: int = 17,
    hour: int = 8,
    gender: Gender = Gender.female,
) -> BirthInfo:
    return BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(year, month, day, hour, 30, tzinfo=timezone(timedelta(hours=8))),
        gender=gender,
        birth_place="Shanghai, China",
        timezone="Asia/Shanghai",
    )


def _birth_info_sample_2() -> BirthInfo:
    return BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(1988, 11, 23, 14, 0, tzinfo=timezone(timedelta(hours=8))),
        gender="male",
        birth_place="Beijing, China",
        timezone="Asia/Shanghai",
    )


def _birth_info_sample_3() -> BirthInfo:
    return BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(2000, 1, 15, 0, 0, tzinfo=timezone(timedelta(hours=8))),
        gender="female",
        birth_place="Guangzhou, China",
        timezone="Asia/Shanghai",
    )


def test_engine_returns_iztro_source() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    assert chart.source == "iztro_py"
    assert chart.source != "stub"


def test_engine_returns_12_palaces() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    assert len(chart.palaces) == 12


def test_engine_palaces_have_chinese_names() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    for palace in chart.palaces:
        assert palace.name
        assert "宫" in palace.name


def test_engine_palaces_have_earthly_branches() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    branches = [p.earthly_branch for p in chart.palaces]
    assert all(b is not None for b in branches)


def test_engine_chart_id_format() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    assert chart.chart_id.startswith("iztro_py-")


def test_engine_chart_id_is_deterministic() -> None:
    engine = ZiweiChartEngine()
    birth = _birth_info()

    chart1 = engine.build_chart(birth)
    chart2 = engine.build_chart(birth)

    assert chart1.chart_id == chart2.chart_id


def test_engine_stars_non_empty() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    total_stars = sum(len(p.stars) for p in chart.palaces)
    assert total_stars > 0, "Real chart should have stars"


def test_engine_sample_2_stable() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info_sample_2())
    assert chart.source == "iztro_py"
    assert len(chart.palaces) == 12


def test_engine_sample_3_stable() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info_sample_3())
    assert chart.source == "iztro_py"
    assert len(chart.palaces) == 12


def test_engine_rejects_unsupported_lunar_calendar() -> None:
    engine = ZiweiChartEngine()
    birth = BirthInfo(
        calendar_type="lunar",
        birth_datetime=datetime(1995, 5, 17, 8, 30, tzinfo=timezone(timedelta(hours=8))),
        gender="female",
        birth_place="Shanghai, China",
        timezone="Asia/Shanghai",
    )

    with pytest.raises(UnsupportedCalendarTypeError, match="Unsupported calendar type: lunar"):
        engine.build_chart(birth)


def test_engine_rejects_unknown_gender() -> None:
    engine = ZiweiChartEngine()
    birth = BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(1995, 5, 17, 8, 30, tzinfo=timezone(timedelta(hours=8))),
        gender="unknown",
        birth_place="Shanghai, China",
        timezone="Asia/Shanghai",
    )

    with pytest.raises(Exception, match="not supported"):
        engine.build_chart(birth)


def test_engine_preserves_birth_info() -> None:
    engine = ZiweiChartEngine()
    birth = _birth_info()
    chart = engine.build_chart(birth)
    assert chart.birth_info_snapshot["gender"] == "female"
    assert chart.birth_info_snapshot["calendar_type"] == "solar"


def test_engine_four_hua_present() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    assert chart.four_hua is not None
    assert chart.four_hua.hua_lu or chart.four_hua.hua_quan or chart.four_hua.hua_ke or chart.four_hua.hua_ji


def test_normalizer_output_structure() -> None:
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    raw = engine.build_chart(_birth_info())
    normalized = normalizer.normalize(raw)

    assert normalized.chart_id == raw.chart_id
    assert normalized.source == "iztro_py"
    assert "12 palaces" in normalized.summary
    assert "Stub" not in normalized.summary
    assert len(normalized.palaces) == 12


def test_normalizer_preserves_palaces() -> None:
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    raw = engine.build_chart(_birth_info())
    normalized = normalizer.normalize(raw)

    for rp, np in zip(raw.palaces, normalized.palaces):
        assert rp.name == np.name
        assert rp.index == np.index
