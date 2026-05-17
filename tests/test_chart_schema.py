from app.schemas.chart import NormalizedChart, Palace, RawChart, Star


def test_palace_serializable() -> None:
    palace = Palace(index=0, name="命宫", stars=[Star(name="紫微")])
    data = palace.model_dump()
    assert data["name"] == "命宫"
    assert len(data["stars"]) == 1


def test_raw_chart_serializable() -> None:
    chart = RawChart(chart_id="test-id", birth_info_snapshot={"key": "value"}, palaces=[])
    data = chart.model_dump()
    assert data["source"] == "stub"
    assert data["chart_id"] == "test-id"


def test_normalized_chart_serializable() -> None:
    chart = NormalizedChart(chart_id="test-id", source="stub", summary="test summary")
    data = chart.model_dump()
    assert data["summary"] == "test summary"
