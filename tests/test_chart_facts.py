from app.engines.chart_facts import build_chart_facts
from app.schemas.chart import FourHua, NormalizedChart, Palace, Star


def _star(name: str, category: str = "major") -> Star:
    return Star(name=name, brightness="庙", category=category)


def _chart(palaces: list[Palace] | None = None, four_hua: FourHua | None = None, **kwargs) -> NormalizedChart:
    p = palaces or []
    defaults = {
        "chart_id": "test",
        "source": "test",
        "summary": "test",
        "palaces": p,
        "four_hua": four_hua,
    }
    defaults.update(kwargs)
    return NormalizedChart(**defaults)


def test_chart_facts_includes_ming_and_body_palace() -> None:
    palaces = [
        Palace(
            index=0,
            name="命宫",
            stars=[_star("紫微")],
            opposite_palace_index=6,
            san_fang_si_zheng_indexes=[0, 4, 6, 8],
            is_empty=False,
        ),
        Palace(
            index=1,
            name="兄弟宫",
            stars=[],
            opposite_palace_index=7,
            san_fang_si_zheng_indexes=[1, 5, 7, 9],
            is_empty=False,
        ),
    ]
    chart = _chart(palaces=palaces, ming_palace_index=0, body_palace_index=1)
    facts = build_chart_facts(chart)
    assert facts["ming_palace"] == "命宫"
    assert facts["body_palace"] == "兄弟宫"


def test_chart_facts_includes_four_hua() -> None:
    four_hua = FourHua(hua_lu="贪狼", hua_quan="太阴", hua_ke="右弼", hua_ji="天机")
    chart = _chart(four_hua=four_hua)
    facts = build_chart_facts(chart)
    assert facts["four_hua"]["hua_lu"] == "贪狼"


def test_chart_facts_palace_contains_major_stars() -> None:
    palaces = [
        Palace(
            index=0,
            name="命宫",
            stars=[_star("紫微"), _star("天府")],
            opposite_palace_index=6,
            san_fang_si_zheng_indexes=[0, 4, 6, 8],
            is_empty=False,
        ),
    ]
    chart = _chart(palaces=palaces)
    facts = build_chart_facts(chart)
    assert facts["palaces"][0]["major_stars"] == ["紫微", "天府"]


def test_chart_facts_empty_palace_shows_borrowing() -> None:
    palaces = [
        Palace(
            index=0,
            name="命宫",
            stars=[],
            opposite_palace_index=6,
            san_fang_si_zheng_indexes=[0, 4, 6, 8],
            is_empty=True,
            borrowed_from_index=6,
            borrowed_major_stars=["天府"],
        ),
        Palace(
            index=6,
            name="迁移宫",
            stars=[_star("天府")],
            opposite_palace_index=0,
            san_fang_si_zheng_indexes=[6, 10, 0, 2],
            is_empty=False,
        ),
    ]
    chart = _chart(palaces=palaces)
    facts = build_chart_facts(chart)
    p0 = facts["palaces"][0]
    assert p0["is_empty"] is True
    assert p0["borrowed_from"]["major_stars"] == ["天府"]
    assert p0["borrowed_from"]["palace_name"] == "迁移宫"


def test_chart_facts_includes_san_fang_si_zheng_names() -> None:
    palaces = [
        Palace(
            index=0,
            name="命宫",
            stars=[_star("紫微")],
            opposite_palace_index=6,
            san_fang_si_zheng_indexes=[0, 4, 6, 8],
            is_empty=False,
        ),
        Palace(
            index=4,
            name="财帛宫",
            stars=[],
            opposite_palace_index=10,
            san_fang_si_zheng_indexes=[4, 8, 10, 0],
            is_empty=False,
        ),
        Palace(
            index=6,
            name="迁移宫",
            stars=[],
            opposite_palace_index=0,
            san_fang_si_zheng_indexes=[6, 10, 0, 2],
            is_empty=False,
        ),
        Palace(
            index=8,
            name="官禄宫",
            stars=[],
            opposite_palace_index=2,
            san_fang_si_zheng_indexes=[8, 0, 2, 4],
            is_empty=False,
        ),
    ]
    chart = _chart(palaces=palaces)
    facts = build_chart_facts(chart)
    assert facts["palaces"][0]["san_fang_si_zheng"] == ["命宫", "财帛宫", "迁移宫", "官禄宫"]


def test_chart_facts_no_fatalistic_content() -> None:
    chart = _chart(
        palaces=[
            Palace(
                index=0,
                name="命宫",
                stars=[_star("紫微")],
                opposite_palace_index=6,
                san_fang_si_zheng_indexes=[0, 4, 6, 8],
                is_empty=False,
            ),
        ]
    )
    facts = build_chart_facts(chart)
    import json

    text = json.dumps(facts, ensure_ascii=False)
    for word in ["必然", "一定", "注定", "宿命", "绝对"]:
        assert word not in text


def test_chart_facts_includes_mutagens() -> None:
    palaces = [
        Palace(
            index=0,
            name="命宫",
            stars=[_star("紫微")],
            four_hua=FourHua(hua_lu="紫微"),
            opposite_palace_index=6,
            san_fang_si_zheng_indexes=[0, 4, 6, 8],
            is_empty=False,
        ),
    ]
    chart = _chart(palaces=palaces)
    facts = build_chart_facts(chart)
    assert facts["palaces"][0]["mutagens"]["化禄"] == "紫微"


# --- evidence_index tests ---


def _full_chart() -> NormalizedChart:
    """Minimal chart with enough data to test all evidence types."""
    return _chart(
        palaces=[
            Palace(
                index=0,
                name="命宫",
                heavenly_stem="甲",
                earthly_branch="寅",
                stars=[_star("紫微"), _star("天府")],
                four_hua=FourHua(hua_lu="紫微"),
                opposite_palace_index=6,
                san_fang_si_zheng_indexes=[0, 4, 6, 8],
                is_empty=False,
            ),
            Palace(
                index=4,
                name="财帛宫",
                stars=[_star("天机")],
                opposite_palace_index=10,
                san_fang_si_zheng_indexes=[4, 8, 10, 0],
                is_empty=False,
            ),
            Palace(
                index=6,
                name="迁移宫",
                stars=[_star("太阳")],
                opposite_palace_index=0,
                san_fang_si_zheng_indexes=[6, 10, 0, 2],
                is_empty=False,
            ),
            Palace(
                index=8,
                name="官禄宫",
                stars=[],
                opposite_palace_index=2,
                san_fang_si_zheng_indexes=[8, 0, 2, 4],
                is_empty=True,
                borrowed_from_index=2,
                borrowed_major_stars=["太阴"],
            ),
            Palace(
                index=2,
                name="夫妻宫",
                stars=[_star("太阴")],
                opposite_palace_index=8,
                san_fang_si_zheng_indexes=[2, 6, 8, 10],
                is_empty=False,
            ),
            Palace(
                index=10,
                name="福德宫",
                stars=[],
                opposite_palace_index=4,
                san_fang_si_zheng_indexes=[10, 2, 4, 6],
                is_empty=False,
            ),
        ],
        four_hua=FourHua(hua_lu="紫微", hua_quan="太阴", hua_ke="右弼", hua_ji="天机"),
        ming_palace_index=0,
        body_palace_index=2,
    )


def test_evidence_index_exists() -> None:
    facts = build_chart_facts(_full_chart())
    assert "evidence_index" in facts
    assert isinstance(facts["evidence_index"], list)
    assert len(facts["evidence_index"]) > 0


def test_evidence_index_has_palace_evidence() -> None:
    facts = build_chart_facts(_full_chart())
    ids = [e["id"] for e in facts["evidence_index"]]
    assert "palace:0" in ids
    assert "palace:6" in ids


def test_evidence_index_has_star_evidence() -> None:
    facts = build_chart_facts(_full_chart())
    ids = [e["id"] for e in facts["evidence_index"]]
    assert "star:0:紫微" in ids
    assert "star:0:天府" in ids
    assert "star:4:天机" in ids


def test_evidence_index_has_mutagen_evidence() -> None:
    facts = build_chart_facts(_full_chart())
    ids = [e["id"] for e in facts["evidence_index"]]
    assert "mutagen:0:hua_lu:紫微" in ids


def test_evidence_index_has_relation_evidence() -> None:
    facts = build_chart_facts(_full_chart())
    ids = [e["id"] for e in facts["evidence_index"]]
    assert "relation:0:opposite:6" in ids
    assert "relation:0:sfsz:0,4,6,8" in ids


def test_evidence_index_has_borrowed_evidence() -> None:
    facts = build_chart_facts(_full_chart())
    ids = [e["id"] for e in facts["evidence_index"]]
    assert "borrowed:8:from:2:太阴" in ids


def test_evidence_item_structure() -> None:
    facts = build_chart_facts(_full_chart())
    for e in facts["evidence_index"]:
        assert "id" in e
        assert "type" in e
        assert "label" in e
        assert isinstance(e["id"], str)
        assert isinstance(e["type"], str)
        assert isinstance(e["label"], str)
