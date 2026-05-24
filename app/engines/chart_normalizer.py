from app.engines.chart_relations import (
    borrowed_from_index,
    borrowed_major_stars,
    is_empty_palace,
    opposite_palace_index,
    san_fang_si_zheng_indexes,
)
from app.schemas.chart import NormalizedChart, Palace, RawChart


class ChartNormalizer:
    def normalize(self, raw_chart: RawChart) -> NormalizedChart:
        by_index = {p.index: p for p in raw_chart.palaces}

        ming_index = None
        body_index = None
        for p in raw_chart.palaces:
            if p.name == "命宫":
                ming_index = p.index
            if p.is_body_palace:
                body_index = p.index

        enriched_palaces = []
        for p in raw_chart.palaces:
            major_names = [s.name for s in p.stars if s.category == "major"]
            empty = is_empty_palace(major_names)
            opp = opposite_palace_index(p.index)
            sfsz = san_fang_si_zheng_indexes(p.index)
            borrowed_idx = borrowed_from_index(p.index) if empty else None
            borrowed_stars = None
            if empty:
                opp_palace = by_index.get(opp)
                opp_majors = [s.name for s in opp_palace.stars if s.category == "major"] if opp_palace else []
                borrowed_stars = borrowed_major_stars(p.index, opp_majors)

            enriched_palaces.append(
                Palace(
                    index=p.index,
                    name=p.name,
                    heavenly_stem=p.heavenly_stem,
                    earthly_branch=p.earthly_branch,
                    stars=p.stars,
                    four_hua=p.four_hua,
                    is_body_palace=p.is_body_palace,
                    opposite_palace_index=opp,
                    san_fang_si_zheng_indexes=sfsz,
                    is_empty=empty,
                    borrowed_from_index=borrowed_idx,
                    borrowed_major_stars=borrowed_stars,
                    decadal=p.decadal,
                )
            )

        return NormalizedChart(
            chart_id=raw_chart.chart_id,
            source=raw_chart.source,
            summary=f"Ziwei chart with {len(raw_chart.palaces)} palaces (source: {raw_chart.source})",
            palaces=enriched_palaces,
            four_hua=raw_chart.four_hua,
            ming_palace_index=ming_index,
            body_palace_index=body_index,
            five_elements_class=(
                raw_chart.metadata.five_elements_class
                if raw_chart.metadata and raw_chart.metadata.five_elements_class
                else None
            ),
            lunar_info=(
                {"lunar_date": raw_chart.metadata.lunar_date}
                if raw_chart.metadata and raw_chart.metadata.lunar_date
                else None
            ),
            metadata=raw_chart.metadata,
            current_age=raw_chart.current_age,
            current_decadal=raw_chart.current_decadal,
        )
