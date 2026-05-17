import uuid

from app.schemas.birth import BirthInfo
from app.schemas.chart import Palace, RawChart


class ZiweiChartEngine:
    def build_chart(self, birth_info: BirthInfo) -> RawChart:
        return RawChart(
            source="stub",
            chart_id=self._generate_chart_id(birth_info),
            birth_info_snapshot=birth_info.model_dump(mode="json"),
            palaces=self._generate_stub_palaces(),
        )

    def _generate_chart_id(self, birth_info: BirthInfo) -> str:
        return f"stub-{uuid.uuid4().hex[:8]}"

    def _generate_stub_palaces(self) -> list[Palace]:
        palace_names = [
            "命宫",
            "兄弟宫",
            "夫妻宫",
            "子女宫",
            "财帛宫",
            "疾厄宫",
            "迁移宫",
            "交友宫",
            "官禄宫",
            "田宅宫",
            "福德宫",
            "父母宫",
        ]
        return [Palace(index=i, name=name) for i, name in enumerate(palace_names)]
