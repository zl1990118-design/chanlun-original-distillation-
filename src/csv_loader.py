"""读取并校验日线 CSV；不代表行情来源已经核实。"""

import csv
from pathlib import Path

from src.market_data import validate_daily_bar


def load_daily_csv(path):
    """读取 CSV，要求列名为 date,open,high,low,close。"""
    required = ("date", "open", "high", "low", "close")
    bars = []
    seen_dates = set()

    with Path(path).open(
        "r", newline="", encoding="utf-8-sig"
    ) as handle:
        reader = csv.DictReader(handle)

        if not reader.fieldnames:
            raise ValueError("CSV 缺少表头")

        reader.fieldnames = [
            name.strip() if name else name
            for name in reader.fieldnames
        ]

        missing = [name for name in required
                   if name not in reader.fieldnames]
        if missing:
            raise ValueError(
                "CSV 缺少字段: " + ", ".join(missing)
            )

        for line_no, row in enumerate(reader, start=2):
            bar = {
                "date": (row.get("date") or "").strip()
            }

            for key in ("open", "high", "low", "close"):
                try:
                    bar[key] = float((row.get(key) or "").strip())
                except ValueError as exc:
                    raise ValueError(
                        f"第 {line_no} 行的 {key} 不是有效数字"
                    ) from exc

            try:
                validate_daily_bar(bar)
            except ValueError as exc:
                raise ValueError(
                    f"第 {line_no} 行数据无效: {exc}"
                ) from exc

            if bar["date"] in seen_dates:
                raise ValueError(
                    f"第 {line_no} 行日期重复: {bar['date']}"
                )

            seen_dates.add(bar["date"])
            bars.append(bar)

    if not bars:
        raise ValueError("CSV 中没有日线数据")

    bars.sort(key=lambda bar: bar["date"])
    return bars
