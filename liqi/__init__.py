"""理气法学习用规则库；通用定格规则尚未讲授。"""

from .chart import analyze_chart
from .solar_time import true_solar_time


def solar_to_four_pillars(*args, **kwargs):
    """公历转四柱；需要 requirements.txt 中的 lunar_python。"""
    from .calendar import solar_to_four_pillars as convert
    return convert(*args, **kwargs)


def beijing_time_to_four_pillars(*args, **kwargs):
    """固定北京时间年月日时分与出生地经度转四柱。"""
    from .calendar import beijing_time_to_four_pillars as convert
    return convert(*args, **kwargs)


def lunar_to_four_pillars(*args, **kwargs):
    """农历转四柱；需要 requirements.txt 中的 lunar_python。"""
    from .calendar import lunar_to_four_pillars as convert
    return convert(*args, **kwargs)


def reference_da_yun(*args, **kwargs):
    """列常见排法的大运参考；需要 lunar_python。"""
    from .fortune import reference_da_yun as calculate
    return calculate(*args, **kwargs)


__all__ = ["analyze_chart", "true_solar_time",
           "solar_to_four_pillars", "beijing_time_to_four_pillars",
           "lunar_to_four_pillars", "reference_da_yun"]
