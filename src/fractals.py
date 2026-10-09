"""三 K 线分型候选识别；规则尚待原文核验。"""


def identify_fractals(bars):
    """返回候选顶底分型。bars 按日期升序排列。

    仅比较相邻三根 K 线，不处理包含关系。
    同高、同低不判定为分型。
    返回的 index 是中间 K 线的位置。
    """
    results = []
    for i in range(1, len(bars) - 1):
        left, mid, right = bars[i - 1], bars[i], bars[i + 1]
        if mid["high"] > left["high"] and mid["high"] > right["high"] and mid["low"] > left["low"] and mid["low"] > right["low"]:
            results.append({"index": i, "type": "top", "date": mid["date"], "price": mid["high"]})
        elif mid["high"] < left["high"] and mid["high"] < right["high"] and mid["low"] < left["low"] and mid["low"] < right["low"]:
            results.append({"index": i, "type": "bottom", "date": mid["date"], "price": mid["low"]})
    return results
