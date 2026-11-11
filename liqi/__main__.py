"""命令行：python3 -m liqi 年柱 月柱 日柱 时柱。"""

import argparse
import json

from .chart import analyze_chart


def main():
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
