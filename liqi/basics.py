"""文件 02 的传统基础表，以及用户明确讲授的月令、时支起步规则。"""

from datetime import time

STEMS = {
    "甲": ("木", "阳"), "乙": ("木", "阴"),
    "丙": ("火", "阳"), "丁": ("火", "阴"),
    "戊": ("土", "阳"), "己": ("土", "阴"),
    "庚": ("金", "阳"), "辛": ("金", "阴"),
    "壬": ("水", "阳"), "癸": ("水", "阴"),
}

# 地支阴阳按文件 02；藏干阴阳须用 STEMS 独立查询。
BRANCHES = {
    "子": ("水", "阳", ("癸",)),
    "丑": ("土", "阴", ("己", "癸", "辛")),
    "寅": ("木", "阳", ("甲", "丙", "戊")),
    "卯": ("木", "阴", ("乙",)),
    "辰": ("土", "阳", ("戊", "乙", "癸")),
    "巳": ("火", "阴", ("丙", "戊", "庚")),
    "午": ("火", "阳", ("丁", "己")),
    "未": ("土", "阴", ("己", "丁", "乙")),
    "申": ("金", "阳", ("庚", "壬", "戊")),
    "酉": ("金", "阴", ("辛",)),
    "戌": ("土", "阳", ("戊", "辛", "丁")),
    "亥": ("水", "阴", ("壬", "甲")),
}

STEM_ORDER = tuple(STEMS)
BRANCH_ORDER = tuple(BRANCHES)
ELEMENTS = ("木", "火", "土", "金", "水")
CONTROLLED = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
GENERATES = dict(zip(ELEMENTS, ELEMENTS[1:] + ELEMENTS[:1]))
STEMS_BY_ELEMENT = {element: [stem for stem, data in STEMS.items() if data[0] == element]
                    for element in ELEMENTS}

GROWTH_STAGES = ("长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养")
GROWTH_BRANCHES = {
    "甲": "亥子丑寅卯辰巳午未申酉戌",
    "乙": "午巳辰卯寅丑子亥戌酉申未",
    "丙": "寅卯辰巳午未申酉戌亥子丑",
    "丁": "酉申未午巳辰卯寅丑子亥戌",
    "戊": "寅卯辰巳午未申酉戌亥子丑",
    "己": "酉申未午巳辰卯寅丑子亥戌",
    "庚": "巳午未申酉戌亥子丑寅卯辰",
    "辛": "子亥戌酉申未午巳辰卯寅丑",
    "壬": "申酉戌亥子丑寅卯辰巳午未",
    "癸": "卯寅丑子亥戌酉申未午巳辰",
}

SEASONS = {
    "冬": ("亥子丑", ("水", "木")),
    "春": ("寅卯辰", ("木", "火")),
    "夏": ("巳午未", ("火", "土")),
    "秋": ("申酉戌", ("金", "水")),
}


def stem_info(stem):
    """查询天干的五行和阴阳。"""
    if stem not in STEMS:
        raise ValueError("无效天干：%s" % stem)
    element, yin_yang = STEMS[stem]
    return {"stem": stem, "element": element, "yin_yang": yin_yang}


def branch_info(branch):
    """查询地支属性、藏干；藏干顺序为本气、中气、余气。"""
    if branch not in BRANCHES:
        raise ValueError("无效地支：%s" % branch)
    element, yin_yang, hidden = BRANCHES[branch]
    return {"branch": branch, "element": element, "yin_yang": yin_yang,
            "hidden_stems": list(hidden), "main_qi": hidden[0]}


def ten_god(day_stem, other_stem):
    """传统排盘十神命名，与理气法实际生克分开。"""
    me = stem_info(day_stem)
    other = stem_info(other_stem)
    a, b = me["element"], other["element"]
    same = me["yin_yang"] == other["yin_yang"]
    if a == b:
        return "比肩" if same else "劫财"
    if GENERATES[a] == b:
        return "食神" if same else "伤官"
    if CONTROLLED[a] == b:
        return "偏财" if same else "正财"
    if CONTROLLED[b] == a:
        return "七杀" if same else "正官"
    return "偏印" if same else "正印"


def month_priority(month_branch):
    """月令优先候选；只表示优先，并非候选之外不可取格。"""
    branch_info(month_branch)
    for season, (members, elements) in SEASONS.items():
        if month_branch in members:
            active = list(elements)
            if month_branch in "辰戌丑未" and "土" not in active:
                active.append("土")
            return {"season": season, "elements": active,
                    "stems": [stem for element in active for stem in STEMS_BY_ELEMENT[element]],
                    "meaning": "优先候选，不是限定"}
    raise AssertionError("地支时令表不完整")


def hour_priority(hour_branch):
    """时支只按本身五行提出候选，不另按季节。"""
    element = branch_info(hour_branch)["element"]
    return {"element": element, "stems": list(STEMS_BY_ELEMENT[element]),
            "meaning": "候选，未规定与月令的取舍"}


def growth_stage(stem, branch):
    """文件 02 所采用的传统十二长生版本，只返回阶段名。"""
    stem_info(stem)
    branch_info(branch)
    return GROWTH_STAGES[GROWTH_BRANCHES[stem].index(branch)]


def zi_phase(corrected_true_solar_time):
    """按已经校正的真太阳时判早晚子；本函数不计算真太阳时。"""
    if not isinstance(corrected_true_solar_time, time):
        raise TypeError("须传入已经校正的真太阳时 datetime.time")
    if corrected_true_solar_time.hour == 23:
        return "晚子"
    if corrected_true_solar_time.hour == 0:
        return "早子"
    return None
