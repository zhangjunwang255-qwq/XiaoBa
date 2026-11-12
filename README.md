# XiaoBa

理气法的 Python 规则库与基础排盘代码。按以下顺序查看源码：

1. [`liqi/__init__.py`](liqi/__init__.py) — 包入口与公开函数。
2. [`liqi/__main__.py`](liqi/__main__.py) — 命令行入口。
3. [`liqi/solar_time.py`](liqi/solar_time.py) — 出生地真太阳时。
4. [`liqi/calendar.py`](liqi/calendar.py) — 公历、农历与四柱排盘，含南半球月支规则。
5. [`liqi/fortune.py`](liqi/fortune.py) — 大运顺逆与起运参考。
6. [`liqi/basics.py`](liqi/basics.py) — 干支、十神等基础资料。
7. [`liqi/relations.py`](liqi/relations.py) — 已确认的干支作用关系。
8. [`liqi/chart.py`](liqi/chart.py) — 盘面事实整理与已讲授例盘。

`__init__.py`、`__main__.py` 是 Python 包要求的特殊文件名；历法模块使用 `calendar.py` 的正确拼写。

依赖见 [`requirements.txt`](requirements.txt)。调用底层公历排盘函数时，须提供带时区的出生时间与出生地经度；南半球还须提供负纬度。南半球大运尚未定义。

中国出生者可运行 `python -m liqi`，按提示输入标准北京时间（`YYYY-MM-DD HH:MM`）及出生地东经度数，直接取得真太阳时和四柱。若原始记录采用夏令时，先核实并换算为标准北京时间。
