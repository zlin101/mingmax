from app.engines.providers.iztro_provider import build_chart_from_iztro
from app.schemas.birth import BirthInfo, CalendarType
from app.schemas.chart import RawChart


class UnsupportedCalendarTypeError(ValueError):
    pass


class ZiweiChartEngine:
    def build_chart(self, birth_info: BirthInfo) -> RawChart:
        if birth_info.calendar_type != CalendarType.solar:
            calendar_type = getattr(birth_info.calendar_type, "value", birth_info.calendar_type)
            raise UnsupportedCalendarTypeError(f"Unsupported calendar type: {calendar_type}")
        return build_chart_from_iztro(birth_info)
