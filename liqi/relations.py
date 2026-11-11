"""已记录的理气法生克、干支组合；只给关系，不判断力量或吉凶。"""

from .basics import CONTROLLED, GENERATES, branch_info, stem_info

STEM_COMBINES = ("甲己", "乙庚", "丙辛", "丁壬", "戊癸")
BRANCH_COMBINES = ("子丑", "寅亥", "卯戌", "辰酉", "巳申", "午未")
BRANCH_CLASHES = ("子午", "丑未", "寅申", "卯酉", "辰戌", "巳亥")
BRANCH_HARMS = ("子未", "丑午", "寅巳", "卯辰", "申亥", "酉戌")
BRANCH_PUNISHMENT_PAIRS = ("子卯", "戌未", "丑戌")
BRANCH_THREE_PUNISHMENTS = ("寅巳申", "丑戌未")
SELF_PUNISHMENT_BRANCHES = "辰午酉亥"  # 是否成立的条件待讲授

# 三合按（长生、帝旺、墓库）；三会只有三支齐全才合出。
THREE_COMBINATIONS = (
    ("木", "亥卯未", ("甲", "乙")),
    ("火", "寅午戌", ("丙", "丁")),
    ("金", "巳酉丑", ("庚", "辛")),
    ("水", "申子辰", ("壬", "癸")),
)
THREE_MEETINGS = (
    ("木", "寅卯辰", ("甲", "乙")),
    ("火", "巳午未", ("丙", "丁")),
    ("金", "申酉戌", ("庚", "辛")),
    ("水", "亥子丑", ("壬", "癸")),
)


def stem_relation(source, target):
    """同阴阳时查询源干对目标干的生、克；其余返回 None。"""
    a, b = stem_info(source), stem_info(target)
    if a["yin_yang"] != b["yin_yang"]:
        return None
    if GENERATES[a["element"]] == b["element"]:
        return "生"
    if CONTROLLED[a["element"]] == b["element"]:
        return "克"
    return None


def _in_pairs(a, b, pairs):
    return any({a, b} == set(pair) for pair in pairs)


def pair_relations(first, second):
    """查询两支明列的合冲穿刑；自刑条件未讲授，仅标明待判。"""
    branch_info(first)
    branch_info(second)
    result = []
    if _in_pairs(first, second, BRANCH_COMBINES):
        result.append("合")
    if _in_pairs(first, second, BRANCH_CLASHES):
        result.append("冲")
    if _in_pairs(first, second, BRANCH_HARMS):
        result.append("穿")
    if _in_pairs(first, second, BRANCH_PUNISHMENT_PAIRS):
        result.append("刑")
    if first == second and first in SELF_PUNISHMENT_BRANCHES:
        result.append("自刑组合（成立条件待讲授）")
    return result


def three_punishments(branches):
    """仅列三支全见的三刑组合；与两两合冲穿如何取舍待讲授。"""
    given = set(branches)
    for branch in given:
        branch_info(branch)
    return [word for word in BRANCH_THREE_PUNISHMENTS if set(word) <= given]


def combine_branches(branches):
    """列出三合、半合、三会合出的干；不推定其取格权重。"""
    given = set(branches)
    for branch in given:
        branch_info(branch)
    result = []
    for element, members, stems in THREE_COMBINATIONS:
        present = [branch for branch in members if branch in given]
        if len(present) == 3:
            result.append({"kind": "三合", "element": element,
                           "branches": list(members), "stems": list(stems)})
        elif len(present) == 2:
            output = [stems[0]] if set(present) == {members[0], members[2]} else list(stems)
            result.append({"kind": "半合", "element": element,
                           "branches": present, "stems": output})
    for element, members, stems in THREE_MEETINGS:
        if set(members) <= given:
            result.append({"kind": "三会", "element": element,
                           "branches": list(members), "stems": list(stems)})
    return result


def taught_three_stem_pattern(stems):
    """仅返回用户明确讲授的三干关系，其他类推仍待核对。"""
    given = list(stems)
    for stem in given:
        stem_info(stem)
    if len(given) != 3 or len(set(given)) != 3:
        return None
    key = frozenset(given)
    patterns = {
        frozenset("庚壬甲"): ["庚生壬", "壬生甲", "不以庚克甲论"],
        frozenset("戊庚壬"): ["戊生庚", "庚生壬", "戊克壬"],
        frozenset("辛癸乙"): ["辛生癸", "癸生乙", "辛仍克乙"],
    }
    if key not in patterns:
        return None
    return {"stems": given, "relations": patterns[key], "source": "用户明确讲授"}
