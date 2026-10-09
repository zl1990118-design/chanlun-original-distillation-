"""CSV 日线分析入口；输出仅为候选结果，规则尚待原文核验。"""

import argparse
import json
from pathlib import Path

from src.csv_loader import load_daily_csv
from src.pipeline import analyze_bars


def build_report(csv_path):
    bars = load_daily_csv(csv_path)
    result = analyze_bars(bars)

    return {
        "input_bar_count": len(bars),
        "merged_bar_count": len(result["merged_bars"]),
        "rule_status": result["rule_status"],
        "candidate_fractals": result["candidate_fractals"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="读取 A 股日线 CSV，输出候选分型"
    )
    parser.add_argument("csv_file", help="日线 CSV 文件路径")
    parser.add_argument(
        "--output",
        help="可选：将结果保存为 JSON 文件",
    )
    args = parser.parse_args()

    try:
        report = build_report(args.csv_file)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print("输入日线数量：", report["input_bar_count"])
    print("合并后 K 线数量：", report["merged_bar_count"])
    print("规则状态：", report["rule_status"])
    print("候选分型：")

    fractals = report["candidate_fractals"]
    if not fractals:
        print("未发现候选分型")
    else:
        for item in fractals:
            print(
                f'{item["date"]} | {item["type"]} | '
                f'价格={item["price"]} | 位置={item["index"]}'
            )

    if args.output:
        Path(args.output).write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print("报告已保存到：", args.output)


if __name__ == "__main__":
    main()
