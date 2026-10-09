import csv
from pathlib import Path
import baostock as bs

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "600000_daily.csv"
FIELDS = "date,open,high,low,close,volume"

lg = bs.login()

try:
    if lg.error_code != "0":
        raise RuntimeError(f"登录失败：{lg.error_msg}")

    print("行情服务器登录成功，正在获取日线数据……")

    rs = bs.query_history_k_data_plus(
        "sh.600000",
        FIELDS,
        "2025-10-01",
        "2026-10-09",
        frequency="d",
        adjustflag="3",
    )

    if rs.error_code != "0":
        raise RuntimeError(f"行情查询失败：{rs.error_msg}")

    rows = []
    while rs.next():
        rows.append(rs.get_row_data())

    if not rows:
        raise RuntimeError("没有获取到行情数据，未写入文件")

    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS.split(","))
        writer.writerows(rows)

    print(f"下载完成：{OUT}")
    print(f"共获取 {len(rows)} 条日线记录")
    print(f"最早日期：{rows[0][0]}")
    print(f"最新日期：{rows[-1][0]}")

finally:
    bs.logout()
