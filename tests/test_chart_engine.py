from datetime import datetime, timedelta, timezone

import pytest

from app.engines.chart_normalizer import ChartNormalizer
from app.engines.ziwei_chart_engine import UnsupportedCalendarTypeError, ZiweiChartEngine
from app.schemas.birth import BirthInfo


def _birth_info() -> BirthInfo:
    return BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(1995, 5, 17, 8, 30, tzinfo=timezone(timedelta(hours=8))),
        gender="female",
        birth_place="Shanghai, China",
        timezone="Asia/Shanghai",
    )


def test_engine_returns_stub_source() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    assert chart.source == "stub"


def test_engine_returns_deterministic_palaces() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    assert len(chart.palaces) == 12
    names = [p.name for p in chart.palaces]
    assert names[0] == "命宫"
    assert names[11] == "父母宫"


def test_engine_chart_id_format() -> None:
    engine = ZiweiChartEngine()
    chart = engine.build_chart(_birth_info())
    assert chart.chart_id.startswith("stub-")


def test_engine_chart_id_is_deterministic() -> None:
    engine = ZiweiChartEngine()
    birth = _birth_info()

    chart1 = engine.build_chart(birth)
    chart2 = engine.build_chart(birth)

    assert chart1.chart_id == chart2.chart_id


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


def test_engine_preserves_birth_info() -> None:
    engine = ZiweiChartEngine()
    birth = _birth_info()
    chart = engine.build_chart(birth)
    assert chart.birth_info_snapshot["gender"] == "female"
    assert chart.birth_info_snapshot["calendar_type"] == "solar"


def test_normalizer_output_structure() -> None:
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    raw = engine.build_chart(_birth_info())
    normalized = normalizer.normalize(raw)

    assert normalized.chart_id == raw.chart_id
    assert normalized.source == "stub"
    assert "12 palaces" in normalized.summary
    assert len(normalized.palaces) == 12


def test_normalizer_preserves_palaces() -> None:
    engine = ZiweiChartEngine()
    normalizer = ChartNormalizer()
    raw = engine.build_chart(_birth_info())
    normalized = normalizer.normalize(raw)

    for rp, np in zip(raw.palaces, normalized.palaces):
        assert rp.name == np.name
        assert rp.index == np.index
