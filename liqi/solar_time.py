"""出生地真太阳时（视太阳时）的近似计算。公式来自 NOAA GML。"""

import calendar
import math
from datetime import datetime, timedelta, timezone


def true_solar_time(birth, longitude):
    """把带时区的出生钟表时换算为出生经度的真太阳时。

    longitude 为东经正、西经负，单位度；纬度不参与真太阳时换算。
    返回的 clock 是无时区的当地视太阳钟面时间，不代表另一 UTC 瞬间。
    NOAA 简化均时差公式是近似值，接近子半、时辰或节令边界时应复核。
    """
    if not isinstance(birth, datetime) or birth.tzinfo is None or birth.utcoffset() is None:
        raise ValueError("出生时间须为带时区的 datetime")
    roundtrip = birth.astimezone(timezone.utc).astimezone(birth.tzinfo)
    if roundtrip.replace(tzinfo=None) != birth.replace(tzinfo=None):
        raise ValueError("出生钟表时落在夏令时跳过的时段")
    if isinstance(longitude, bool) or not isinstance(longitude, (int, float)):
        raise ValueError("经度须为数值，东经为正")
    longitude = float(longitude)
    if not math.isfinite(longitude) or not -180 <= longitude <= 180:
        raise ValueError("经度须在 -180 到 180 度之间")

    days_in_year = 366 if calendar.isleap(birth.year) else 365
    hour = (birth.hour + birth.minute / 60 + birth.second / 3600
            + birth.microsecond / 3_600_000_000)
    gamma = 2 * math.pi / days_in_year * (birth.timetuple().tm_yday - 1 + (hour - 12) / 24)
    equation = 229.18 * (
        0.000075 + 0.001868 * math.cos(gamma) - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma) - 0.040849 * math.sin(2 * gamma)
    )
    tz_hours = birth.utcoffset().total_seconds() / 3600
    longitude_offset = 4 * longitude - 60 * tz_hours
    total_offset = longitude_offset + equation
    local_clock = birth.replace(tzinfo=None)
    apparent_clock = local_clock + timedelta(minutes=total_offset)
    return {
        "clock": apparent_clock,
        "equation_of_time_minutes": equation,
        "longitude_correction_minutes": longitude_offset,
        "total_offset_minutes": total_offset,
        "method": "NOAA GML 近似均时差 + 经度时差",
    }
