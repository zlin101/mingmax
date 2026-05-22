from app.schemas.chart import NormalizedChart, RawChart


class ChartNormalizer:
    def normalize(self, raw_chart: RawChart) -> NormalizedChart:
        palace_count = len(raw_chart.palaces)
        return NormalizedChart(
            chart_id=raw_chart.chart_id,
            source=raw_chart.source,
            summary=f"Ziwei chart with {palace_count} palaces (source: {raw_chart.source})",
            palaces=raw_chart.palaces,
            four_hua=raw_chart.four_hua,
        )
