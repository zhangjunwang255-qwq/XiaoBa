"""无参数时询问北京时间排盘；四柱参数仍用于已排好命盘的分析。"""

import argparse
import json
import sys
from datetime import datetime

from .chart import analyze_chart
from .calendar import beijing_time_to_four_pillars


def _interactive_beijing_chart():
    try:
        birth_text = input("北京时间出生年月日时分（YYYY-MM-DD HH:MM）：")
        birth = datetime.strptime(birth_text.strip(), "%Y-%m-%d %H:%M")
        longitude = float(input("出生地东经度数："))
        result = beijing_time_to_four_pillars(
            birth.year, birth.month, birth.day, birth.hour, birth.minute, longitude
        )
    except (ValueError, EOFError) as exc:
        raise SystemExit("输入错误：请提供有效的北京时间和出生地经度。") from exc
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) == 1:
        _interactive_beijing_chart()
        return
    parser = argparse.ArgumentParser(description="理气法已确认规则查询：输入已排好的四柱")
    for name in ("year", "month", "day", "hour"):
        parser.add_argument(name, help=name + "柱，如壬午")
    args = parser.parse_args()
    try:
        result = analyze_chart(args.year, args.month, args.day, args.hour)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
