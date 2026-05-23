from app.schemas.chart import NormalizedChart, Palace


def build_chart_facts(chart: NormalizedChart) -> dict:
    by_index: dict[int, Palace] = {p.index: p for p in chart.palaces}

    palace_facts = []
    evidence_index: list[dict] = []

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

        # Evidence: palace existence
        evidence_index.append({"id": f"palace:{p.index}", "type": "palace", "label": f"{p.name}(index {p.index})"})

        # Evidence: major stars
        for star_name in major_stars:
            evidence_index.append(
                {"id": f"star:{p.index}:{star_name}", "type": "star", "label": f"{star_name}在{p.name}"}
            )

        # Evidence: mutagens in palace
        for label, star_name in mutagens.items():
            field_map = {"化禄": "hua_lu", "化权": "hua_quan", "化科": "hua_ke", "化忌": "hua_ji"}
            field = field_map[label]
            evidence_index.append(
                {
                    "id": f"mutagen:{p.index}:{field}:{star_name}",
                    "type": "mutagen",
                    "label": f"{star_name}{label}在{p.name}",
                }
            )

        # Evidence: opposite palace
        if p.opposite_palace_index is not None:
            evidence_index.append(
                {
                    "id": f"relation:{p.index}:opposite:{p.opposite_palace_index}",
                    "type": "relation",
                    "label": (
                        f"{p.name}对宫{by_index[p.opposite_palace_index].name}"
                        if p.opposite_palace_index in by_index
                        else f"{p.name}对宫index {p.opposite_palace_index}"
                    ),
                }
            )

        # Evidence: san fang si zheng
        if p.san_fang_si_zheng_indexes:
            sfsz_key = ",".join(str(i) for i in p.san_fang_si_zheng_indexes)
            evidence_index.append(
                {
                    "id": f"relation:{p.index}:sfsz:{sfsz_key}",
                    "type": "relation",
                    "label": f"{p.name}三方四正",
                }
            )

        # Evidence: borrowed stars
        if p.is_empty and p.borrowed_major_stars:
            for borrowed_star in p.borrowed_major_stars:
                from_idx = p.borrowed_from_index
                evidence_index.append(
                    {
                        "id": f"borrowed:{p.index}:from:{from_idx}:{borrowed_star}",
                        "type": "borrowed",
                        "label": f"{p.name}(空宫)借{borrowed_star}",
                    }
                )

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
        "evidence_index": evidence_index,
    }
    if chart.five_elements_class:
        result["five_elements_class"] = chart.five_elements_class

    return result
