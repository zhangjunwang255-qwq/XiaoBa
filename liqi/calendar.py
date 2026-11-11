"""公历、农历转四柱；历法使用 lunar_python，真太阳时使用 solar_time。"""

from datetime import datetime, timedelta, timezone
from math import isfinite
from zoneinfo import ZoneInfo

from lunar_python import Lunar, Solar

from .basics import zi_phase
from .relations import BRANCH_CLASHES
from .solar_time import true_solar_time

CHINA_TIMEZONE = ZoneInfo("Asia/Shanghai")
CALENDAR_TIMEZONE = timezone(timedelta(hours=8))  # 历法库节气表的固定北京时间


def _library_solar(clock):
    return Solar.fromYmdHms(clock.year, clock.month, clock.day,
                            clock.hour, clock.minute, clock.second)


def _check_china_clock(civil):
    """农历输入没有 fold 参数，拒绝历史夏令时的不存在/重复钟表时。"""
    plain = civil.replace(tzinfo=None)
    roundtrip = civil.astimezone(timezone.utc).astimezone(CHINA_TIMEZONE)
    if roundtrip.replace(tzinfo=None) != plain:
        raise ValueError("出生钟表时落在夏令时跳过的时段")
    other = civil.replace(fold=1)
    if other.utcoffset() != civil.utcoffset():
        other_roundtrip = other.astimezone(timezone.utc).astimezone(CHINA_TIMEZONE)
        if other_roundtrip.replace(tzinfo=None) == plain:
            raise ValueError("出生钟表时落在夏令时重复的时段；请用带时区和 fold 的公历时间输入")


def _hemisphere(latitude):
    if latitude is None:
        return "北"
    if isinstance(latitude, bool):
        raise ValueError("纬度须为非零的 -90 至 90 度数值")
    try:
        latitude = float(latitude)
    except (TypeError, ValueError) as exc:
        raise ValueError("纬度须为非零的 -90 至 90 度数值") from exc
    if not isfinite(latitude) or latitude == 0 or not -90 <= latitude <= 90:
        raise ValueError("纬度须为非零的 -90 至 90 度数值")
    return "南" if latitude < 0 else "北"


def _opposite_branch(branch):
    for first, second in BRANCH_CLASHES:
        if branch == first:
            return second
        if branch == second:
            return first
    raise ValueError("无效地支：%s" % branch)


def solar_to_four_pillars(birth, longitude, latitude=None):
    """公历出生瞬间与出生经度转年、月、日、时四柱。

    birth 必须带实际出生地时区。年/月按中国历法节气实际交接瞬间；
    负纬度为南半球，月柱只把地支换成相冲支；不传纬度默认北半球。
    日/时按出生地真太阳时。晚子日柱留在当日，时干按次日日干起。
    """
    hemisphere = _hemisphere(latitude)
    solar_result = true_solar_time(birth, longitude)
    apparent = solar_result["clock"]
    china_clock = birth.astimezone(CALENDAR_TIMEZONE)
    calendar_eight = _library_solar(china_clock).getLunar().getEightChar()
    apparent_eight = _library_solar(apparent).getLunar().getEightChar()
    apparent_eight.setSect(2)  # 晚子日柱属当日；库的时干按次日日干起。
    north_month = calendar_eight.getMonth()
    month = north_month if hemisphere == "北" else north_month[0] + _opposite_branch(north_month[1])
    pillars = [calendar_eight.getYear(), month,
               apparent_eight.getDay(), apparent_eight.getTime()]
    return {
        "civil_time": birth.isoformat(),
        "true_solar_time": apparent.isoformat(timespec="seconds"),
        "longitude": float(longitude),
        "latitude": None if latitude is None else float(latitude),
        "hemisphere": hemisphere,
        "northern_month": north_month,
        "pillars": pillars,
        "year": pillars[0], "month": pillars[1],
        "day": pillars[2], "hour": pillars[3],
        "zi_phase": zi_phase(apparent.time()),
        "solar_time_offset_minutes": solar_result["total_offset_minutes"],
        "equation_of_time_minutes": solar_result["equation_of_time_minutes"],
        "longitude_correction_minutes": solar_result["longitude_correction_minutes"],
        "accuracy_note": "真太阳时采用 NOAA 近似均时差；贴近子半、时辰或节令交接时须复核",
        "rules": {
            "year": "立春实际交接时刻换年",
            "month": "十二节实际交接时刻换月",
            "southern_month": "南半球保留北半球月干，月支换成相冲支",
            "day": "真太阳时子半（00:00）换日",
            "late_zi_hour_stem": "23:00—24:00 以次日日干起时干",
        },
    }


def lunar_to_four_pillars(lunar_year, lunar_month, lunar_day,
                          hour, minute, second, longitude, is_leap=False,
                          latitude=None):
    """中国农历日期与中国当地民用时转四柱；闰月须设 is_leap=True。

    农历日按中国历法（Asia/Shanghai）解释。出生地点经度可另填；
    如输入是其他时区的本地钟表时，应先换算成公历并调用上面的函数。
    """
    if (not 1 <= lunar_month <= 12 or not 1 <= lunar_day <= 30
            or not 0 <= hour <= 23 or not 0 <= minute <= 59 or not 0 <= second <= 59):
        raise ValueError("无效农历月日或时分秒")
    signed_month = -lunar_month if is_leap else lunar_month
    try:
        lunar = Lunar.fromYmdHms(lunar_year, signed_month, lunar_day,
                                 hour, minute, second)
        solar = lunar.getSolar()
    except Exception as exc:  # lunar_python 对不存在的闰月抛出普通 Exception。
        raise ValueError("无效农历日期") from exc
    if (lunar.getYear(), lunar.getMonth(), lunar.getDay()) != (
            lunar_year, signed_month, lunar_day):
        raise ValueError("无效农历日期")
    civil = datetime(solar.getYear(), solar.getMonth(), solar.getDay(),
                     hour, minute, second, tzinfo=CHINA_TIMEZONE)
    _check_china_clock(civil)
    result = solar_to_four_pillars(civil, longitude, latitude=latitude)
    result["lunar_input"] = {"year": lunar_year, "month": lunar_month,
                             "day": lunar_day, "is_leap": bool(is_leap)}
    return result
