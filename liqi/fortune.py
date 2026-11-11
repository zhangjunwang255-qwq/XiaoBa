"""常见大运排法的参考输出；目前不是用户师传理气法的已授规则。"""

from datetime import datetime

from .calendar import CALENDAR_TIMEZONE, _library_solar


def reference_da_yun(birth, gender, count=10, sect=1):
    """按 lunar_python 常见排法列大运。

    阳年男、阴年女顺行，其余逆行；sect=1 按整日/时辰折算起运，
    sect=2 按分钟折算。返回年月与虚岁只作历法库参考，不作理气法断命。
    """
    if not isinstance(birth, datetime) or birth.tzinfo is None or birth.utcoffset() is None:
        raise ValueError("出生时间须为带时区的 datetime")
    if gender not in ("男", "女"):
        raise ValueError("gender 须为『男』或『女』")
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 20:
        raise ValueError("count 须为 1—20 的整数")
    if sect not in (1, 2):
        raise ValueError("sect 须为 1（整日/时辰）或 2（分钟）")
    china_clock = birth.astimezone(CALENDAR_TIMEZONE)
    eight = _library_solar(china_clock).getLunar().getEightChar()
    eight.setSect(2)  # 日柱晚子规则，与本项目一致；大运顺逆看年干。
    yun = eight.getYun(1 if gender == "男" else 0, sect=sect)
    start = yun.getStartSolar()
    periods = []
    for item in yun.getDaYun(count + 1)[1:]:
        index = item.getIndex()
        periods.append({
            "number": index,
            "gan_zhi": item.getGanZhi(),
            "start_time": start.nextYear((index - 1) * 10).toYmdHms(),
            "end_exclusive": start.nextYear(index * 10).toYmdHms(),
            "start_year": item.getStartYear(),
            "end_year": item.getEndYear(),
            "start_age_virtual": item.getStartAge(),
            "end_age_virtual": item.getEndAge(),
        })
    return {
        "gender": gender,
        "direction": "顺" if yun.isForward() else "逆",
        "start_after_birth": {"years": yun.getStartYear(), "months": yun.getStartMonth(),
                              "days": yun.getStartDay(), "hours": yun.getStartHour()},
        "start_time": start.toYmdHms(),
        "month_pillar": eight.getMonth(),
        "method": "lunar_python sect=%d；阳年男/阴年女顺，其余逆；三天折一年" % sect,
        "status": "常见排法参考，非已讲授的理气法大运规则",
        "periods": periods,
    }
