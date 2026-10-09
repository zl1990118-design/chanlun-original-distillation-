"""候选分型识别；规则仍需按缠论原文核验。"""


def identify_fractals(bars):
    """返回候选分型；顶用最高价来源日期，底用最低价来源日期。"""
    results = []

    for i in range(1, len(bars) - 1):
        left, mid, right = bars[i - 1], bars[i], bars[i + 1]

        if (
            mid["high"] > left["high"]
            and mid["high"] > right["high"]
            and mid["low"] > left["low"]
            and mid["low"] > right["low"]
        ):
            results.append({
                "index": i,
                "type": "top",
                "date": mid.get("high_date") or mid["date"],
                "price": mid["high"],
            })

        elif (
            mid["high"] < left["high"]
            and mid["high"] < right["high"]
            and mid["low"] < left["low"]
            and mid["low"] < right["low"]
        ):
            results.append({
                "index": i,
                "type": "bottom",
                "date": mid.get("low_date") or mid["date"],
                "price": mid["low"],
            })

    return results
