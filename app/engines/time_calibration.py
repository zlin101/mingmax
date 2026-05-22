import math
from datetime import datetime, timedelta


def infer_longitude_from_timezone(local_dt: datetime) -> float:
    tz = local_dt.tzinfo
    if tz is None:
        return 120.0
    offset_hours = tz.utcoffset(local_dt).total_seconds() / 3600
    return offset_hours * 15


def true_solar_time_offset(local_dt: datetime, longitude: float) -> timedelta:
    day_of_year = local_dt.timetuple().tm_yday
    angle = 2 * math.pi * (day_of_year - 81) / 364
    eot_minutes = 9.87 * math.sin(2 * angle) - 7.53 * math.cos(angle) - 1.5 * math.sin(angle)
    tz = local_dt.tzinfo
    tz_offset_hours = tz.utcoffset(local_dt).total_seconds() / 3600 if tz else 0
    longitude_correction = (longitude - tz_offset_hours * 15) * 4
    return timedelta(minutes=eot_minutes + longitude_correction)
