"""把用户给定的四柱整理为可核对事实；通用定格法尚未讲授。"""

from itertools import combinations

from .basics import branch_info, hour_priority, month_priority, stem_info, ten_god
from .relations import (
    STEM_COMBINES,
    combine_branches,
    pair_relations,
    stem_relation,
    taught_three_stem_pattern,
    three_punishments,
)

TAUGHT_CHART = ("壬午", "戊申", "辛酉", "庚子")
POSITIONS = ("year", "month", "day", "hour")


def _pillar(word):
    if not isinstance(word, str) or len(word) != 2:
        raise ValueError("四柱须各为一个天干加一个地支：%r" % word)
    stem_info(word[0])
    branch_info(word[1])
    return word[0], word[1]


def _source_list(stems, branches):
    """列明透干与各支本气；仅列资格，不排序和定格。"""
    result = []
    for i, (stem, branch) in enumerate(zip(stems, branches)):
        if i != 2:  # 日干只用于排十神，不进入断命候选。
            result.append({"stem": stem, "source": POSITIONS[i] + "_stem"})
        result.append({"stem": branch_info(branch)["main_qi"],
                       "source": POSITIONS[i] + "_branch_main_qi"})
    return result


def analyze_chart(year, month, day, hour):
    """整理四柱，不为未讲授的命盘自动判定格神、用神或吉凶。"""
    words = (year, month, day, hour)
    parsed = [_pillar(word) for word in words]
    stems = [item[0] for item in parsed]
    branches = [item[1] for item in parsed]
    judgment_stems = [stems[i] for i in (0, 1, 3)]
    taught_pattern = taught_three_stem_pattern(judgment_stems)
    visible_ten_gods = {POSITIONS[i] + "_stem": ten_god(stems[2], stem)
                        for i, stem in enumerate(stems) if i != 2}
    hidden_ten_gods = {
        POSITIONS[i] + "_branch": [
            {"stem": hidden, "ten_god": ten_god(stems[2], hidden)}
            for hidden in branch_info(branch)["hidden_stems"]
        ] for i, branch in enumerate(branches)
    }
    branch_pairs = []
    for i, j in combinations(range(4), 2):
        relations = pair_relations(branches[i], branches[j])
        if relations:
            branch_pairs.append({"positions": [POSITIONS[i], POSITIONS[j]],
                                 "branches": [branches[i], branches[j]],
                                 "relations": relations})
    stem_pairs = []
    for i, j in combinations((0, 1, 3), 2):
        pair = stems[i] + stems[j]
        if any(set(pair) == set(item) for item in STEM_COMBINES):
            stem_pairs.append({"stems": list(pair), "relation": "合",
                               "meaning": "成合条件及后续用法待讲授"})
    basic_stem_relations = []
    for source in judgment_stems:
        for target in judgment_stems:
            if source != target:
                relation = stem_relation(source, target)
                if relation and not (
                    taught_pattern is not None
                    and set(judgment_stems) == {"庚", "壬", "甲"}
                    and source == "庚" and target == "甲"
                ):
                    basic_stem_relations.append(source + relation + target)
    conclusion = {"status": "待讲授", "ge_shen": None, "yong_shen": [],
                  "reason": "目前未讲授通用的取格、取用神及各关系权重"}
    unresolved = ["月令、时支、透干、本气和合冲关系之间的取舍待讲授",
                  "真太阳时校正、日柱与时干排法待讲授；此函数仅接收已排四柱"]
    if words == TAUGHT_CHART:
        conclusion = {
            "status": "已讲授实例", "ge_shen": "壬", "ge_name": "壬水格",
            "yong_shen": ["己", "庚"], "source": "用户明确讲授的此盘",
            "reason": ["申月金水旺，子时支属水", "戊生庚，庚生壬，气聚壬水",
                       "午中己克子中癸，故不取癸", "己和庚为本盘最大的用神"],
        }
        unresolved.append("戊克壬在本例聚气定格中如何参与判断待讲授")
    return {
        "pillars": dict(zip(POSITIONS, words)),
        "day_stem_role": "只用于定十神；断命比较时忽略日干",
        "ten_gods": visible_ten_gods,
        "hidden_stem_ten_gods": hidden_ten_gods,
        "judgment_stems": judgment_stems,
        "month": month_priority(branches[1]),
        "hour": hour_priority(branches[3]),
        "candidate_sources": _source_list(stems, branches),
        "stem_relations": basic_stem_relations,
        "taught_three_stem_pattern": taught_pattern,
        "stem_combinations": stem_pairs,
        "branch_relations": branch_pairs,
        "three_punishments": three_punishments(branches),
        "branch_combinations": combine_branches(branches),
        "conclusion": conclusion,
        "unresolved": unresolved,
    }
