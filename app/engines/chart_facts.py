from app.schemas.chart import NormalizedChart, Palace


def build_chart_facts(chart: NormalizedChart) -> dict:
    by_index: dict[int, Palace] = {p.index: p for p in chart.palaces}

    palace_facts = []
    for p in chart.palaces:
        major_stars = [s.name for s in p.stars if s.category == "major"]
        minor_stars = [s.name for s in p.stars if s.category == "minor"]
        adjective_stars = [s.name for s in p.stars if s.category == "adjective"]
        mutagens = {}
        if p.four_hua:
            for field, label in [
                ("hua_lu", "化禄"),
                ("hua_quan", "化权"),
                ("hua_ke", "化科"),
                ("hua_ji", "化忌"),
            ]:
                val = getattr(p.four_hua, field, None)
                if val:
                    mutagens[label] = val

        fact: dict = {
            "index": p.index,
            "name": p.name,
            "major_stars": major_stars,
        }
        if minor_stars:
            fact["minor_stars"] = minor_stars
        if adjective_stars:
            fact["adjective_stars"] = adjective_stars
        if mutagens:
            fact["mutagens"] = mutagens
        if p.is_body_palace:
            fact["is_body_palace"] = True
        if p.is_empty:
            fact["is_empty"] = True
            if p.borrowed_major_stars:
                opp = by_index.get(p.borrowed_from_index) if p.borrowed_from_index is not None else None
                fact["borrowed_from"] = {
                    "palace_name": opp.name if opp else None,
                    "major_stars": p.borrowed_major_stars,
                }
        if p.opposite_palace_index is not None:
            opp = by_index.get(p.opposite_palace_index)
            fact["opposite_palace"] = opp.name if opp else None
        if p.san_fang_si_zheng_indexes:
            fact["san_fang_si_zheng"] = [by_index[idx].name for idx in p.san_fang_si_zheng_indexes if idx in by_index]
        palace_facts.append(fact)

    result: dict = {
        "ming_palace": (
            by_index[chart.ming_palace_index].name
            if chart.ming_palace_index is not None and chart.ming_palace_index in by_index
            else None
        ),
        "body_palace": (
            by_index[chart.body_palace_index].name
            if chart.body_palace_index is not None and chart.body_palace_index in by_index
            else None
        ),
        "four_hua": chart.four_hua.model_dump(exclude_none=True) if chart.four_hua else {},
        "palaces": palace_facts,
    }
    if chart.five_elements_class:
        result["five_elements_class"] = chart.five_elements_class

    return result
