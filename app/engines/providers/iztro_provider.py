import hashlib
from datetime import timedelta
from zoneinfo import ZoneInfo

from iztro_py import astro

from app.engines.errors import UnsupportedGenderError
from app.schemas.birth import BirthInfo, Gender
from app.schemas.chart import FourHua, Palace, RawChart, Star

GENDER_MAP = {
    Gender.male: "男",
    Gender.female: "女",
}

SOURCE = "iztro_py"

_EQUATION_OF_TIME_APPROX = [
    -3,
    -6,
    -9,
    -12,
    -14,
    -15,
    -14,
    -10,
    -4,
    2,
    7,
    10,
    11,
    9,
    5,
    0,
    -5,
    -9,
    -12,
    -13,
    -12,
    -9,
    -5,
    0,
    5,
    10,
    13,
    14,
    13,
    10,
    6,
    1,
    -4,
    -9,
    -13,
    -14,
    -13,
    -10,
    -5,
    0,
    4,
    9,
    12,
    14,
    13,
    10,
    6,
    1,
    -4,
    -9,
    -13,
    -14,
    -13,
    -10,
    -6,
    -1,
    4,
    9,
    13,
    14,
    13,
    10,
    6,
    1,
    -4,
    -9,
    -13,
    -14,
    -13,
    -10,
    -6,
    -1,
    4,
    9,
    13,
    14,
    14,
    11,
    7,
    2,
    -3,
    -8,
    -12,
    -14,
    -14,
    -12,
    -8,
    -4,
    1,
    6,
    10,
    13,
    14,
    14,
    12,
    8,
    4,
    -1,
    -5,
    -9,
    -12,
    -14,
    -14,
    -12,
    -9,
    -5,
    0,
    5,
    9,
    13,
    14,
    14,
    12,
    8,
    4,
    -1,
    -6,
    -10,
    -13,
    -14,
    -13,
    -11,
    -7,
    -2,
    3,
    8,
    12,
    14,
    14,
    13,
    10,
    6,
    1,
    -4,
    -8,
    -12,
    -14,
    -14,
    -13,
    -10,
    -6,
    -1,
    4,
    8,
    12,
    14,
    14,
    13,
    10,
    6,
    1,
    -4,
    -9,
    -13,
    -15,
    -14,
    -12,
    -9,
    -5,
    0,
    5,
    10,
    13,
    15,
    14,
    12,
    9,
    5,
    0,
    -5,
    -10,
    -13,
    -15,
    -15,
    -13,
    -9,
    -5,
    0,
    5,
    10,
    13,
    15,
    15,
    13,
    9,
    4,
    -1,
    -6,
    -10,
    -13,
    -15,
    -15,
    -13,
    -10,
    -6,
    -1,
    4,
    9,
    12,
    14,
    15,
    14,
    12,
    8,
    4,
    -1,
    -6,
    -10,
    -13,
    -15,
    -15,
    -13,
    -10,
    -6,
    -1,
    4,
    9,
    13,
    15,
    15,
    13,
    10,
    6,
    1,
    -4,
    -9,
    -13,
    -15,
    -15,
    -14,
    -11,
    -7,
    -2,
    3,
    8,
    12,
    14,
    15,
    14,
    12,
    8,
    4,
    -1,
    -6,
    -10,
    -13,
    -15,
    -15,
    -14,
    -11,
    -7,
    -2,
    3,
    8,
    12,
    14,
    15,
    14,
    12,
    9,
    5,
    0,
    -5,
    -10,
    -13,
    -15,
    -15,
    -14,
    -12,
    -8,
    -3,
    2,
    7,
    11,
    14,
    15,
    14,
    12,
    8,
    4,
    -1,
    -6,
    -10,
    -14,
    -15,
    -14,
    -12,
    -8,
    -4,
    1,
    6,
    10,
    14,
    15,
    14,
    13,
    9,
    5,
    0,
    -5,
    -10,
    -13,
    -15,
    -15,
    -14,
    -11,
    -7,
    -2,
    3,
    8,
    12,
    14,
    15,
    14,
    12,
    8,
    4,
    -1,
    -5,
    -10,
    -13,
    -15,
    -15,
    -14,
    -11,
    -7,
    -2,
    3,
    8,
    12,
    14,
    15,
    14,
    12,
    9,
    5,
    0,
    -4,
    -9,
    -13,
    -15,
    -14,
    -13,
    -10,
    -6,
    -1,
]


def _true_solar_time_offset(local_dt, longitude: float) -> timedelta:
    day_of_year = local_dt.timetuple().tm_yday
    idx = min(day_of_year - 1, len(_EQUATION_OF_TIME_APPROX) - 1)
    eot_minutes = _EQUATION_OF_TIME_APPROX[idx]
    tz = local_dt.tzinfo
    tz_offset_hours = tz.utcoffset(local_dt).total_seconds() / 3600 if tz else 0
    longitude_correction = (longitude - tz_offset_hours * 15) * 4
    total_minutes = eot_minutes + longitude_correction
    return timedelta(minutes=total_minutes)


def _get_local_date_hour(birth_info: BirthInfo) -> tuple[str, int]:
    tz = ZoneInfo(birth_info.timezone)
    local_dt = birth_info.birth_datetime.astimezone(tz)

    if birth_info.longitude is not None:
        tst_offset = _true_solar_time_offset(local_dt, birth_info.longitude)
        true_solar_dt = local_dt + tst_offset
        date_str = true_solar_dt.strftime("%Y-%m-%d")
        hour = true_solar_dt.hour
    else:
        date_str = local_dt.strftime("%Y-%m-%d")
        hour = local_dt.hour

    return date_str, hour


def _map_gender(gender: Gender) -> str:
    mapped = GENDER_MAP.get(gender)
    if mapped is None:
        raise UnsupportedGenderError(
            f"Gender '{gender.value}' is not supported by the chart engine. "
            f"Supported: {', '.join(g.value for g in GENDER_MAP)}"
        )
    return mapped


def _parse_stars(iztro_stars: list, category: str) -> list[Star]:
    stars = []
    for s in iztro_stars:
        name = s.translate_name() if hasattr(s, "translate_name") else str(s.name)
        brightness = s.translate_brightness() if (hasattr(s, "translate_brightness") and s.brightness) else None
        stars.append(Star(name=name, brightness=brightness, category=category))
    return stars


def _extract_four_hua(palaces: list) -> FourHua | None:
    hua_map: dict[str, str] = {}
    for palace in palaces:
        for s in palace.major_stars:
            if s.mutagen:
                star_name = s.translate_name() if hasattr(s, "translate_name") else str(s.name)
                mutagen_map = {"禄": "hua_lu", "权": "hua_quan", "科": "hua_ke", "忌": "hua_ji"}
                field = mutagen_map.get(s.mutagen)
                if field:
                    hua_map[field] = star_name
    if not hua_map:
        return None
    return FourHua(**hua_map)


def build_chart_from_iztro(birth_info: BirthInfo) -> RawChart:
    gender = _map_gender(birth_info.gender)
    date_str, hour = _get_local_date_hour(birth_info)
    chart = astro.by_solar_hour(date_str, hour, gender)

    palaces = []
    for i, p in enumerate(chart.palaces):
        palace_name = p.translate_name() if hasattr(p, "translate_name") else str(p.name)
        heavenly_stem = p.translate_heavenly_stem() if hasattr(p, "translate_heavenly_stem") else None
        earthly_branch = p.translate_earthly_branch() if hasattr(p, "translate_earthly_branch") else None

        stars = _parse_stars(p.major_stars, "major")
        stars += _parse_stars(p.minor_stars, "minor")
        stars += _parse_stars(p.adjective_stars, "adjective")

        is_body = hasattr(p, "is_body_palace") and p.is_body_palace

        palace_four_hua = None
        for s in p.major_stars:
            if s.mutagen:
                mutagen_map = {"禄": "hua_lu", "权": "hua_quan", "科": "hua_ke", "忌": "hua_ji"}
                field = mutagen_map.get(s.mutagen)
                if field:
                    star_name = s.translate_name() if hasattr(s, "translate_name") else str(s.name)
                    palace_four_hua = FourHua(**{field: star_name})
                    break

        palaces.append(
            Palace(
                index=i,
                name=palace_name,
                heavenly_stem=heavenly_stem,
                earthly_branch=earthly_branch,
                stars=stars,
                four_hua=palace_four_hua,
                is_body_palace=is_body,
            )
        )

    four_hua = _extract_four_hua(chart.palaces)

    payload = birth_info.model_dump_json()
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]

    return RawChart(
        source=SOURCE,
        chart_id=f"{SOURCE}-{digest}",
        birth_info_snapshot=birth_info.model_dump(mode="json"),
        palaces=palaces,
        four_hua=four_hua,
    )
