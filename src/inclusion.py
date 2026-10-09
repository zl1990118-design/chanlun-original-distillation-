"""包含K线合并候选实现；规则仍需按缠论原文核验。"""


def merge_inclusions(bars):
    result = []

    for bar in bars:
        if "high" not in bar or "low" not in bar:
            raise ValueError("missing high or low")

        high = float(bar["high"])
        low = float(bar["low"])

        if high < low:
            raise ValueError("high < low")

        current = dict(bar)
        current["high"] = high
        current["low"] = low
        current["high_date"] = (
            current.get("high_date") or current.get("date")
        )
        current["low_date"] = (
            current.get("low_date") or current.get("date")
        )

        if not result:
            result.append(current)
            continue

        previous = result[-1]
        ph, pl = previous["high"], previous["low"]

        contains = (
            (ph >= high and pl <= low)
            or (high >= ph and low <= pl)
        )

        if not contains:
            result.append(current)
            continue

        # 没有更早的K线，无法依据前序方向进行合并。
        if len(result) < 2:
            raise ValueError(
                "无法确定包含合并方向：缺少前序方向依据"
            )

        prior = result[-2]

        if (
            previous["high"] > prior["high"]
            and previous["low"] > prior["low"]
        ):
            direction = "up"
        elif (
            previous["high"] < prior["high"]
            and previous["low"] < prior["low"]
        ):
            direction = "down"
        else:
            raise ValueError(
                "无法确定包含合并方向：前序K线关系异常"
            )

        if direction == "up":
            if high > ph:
                previous["high_date"] = current["high_date"]
            if low > pl:
                previous["low_date"] = current["low_date"]

            previous["high"] = max(ph, high)
            previous["low"] = max(pl, low)

        elif direction == "down":
            if high < ph:
                previous["high_date"] = current["high_date"]
            if low < pl:
                previous["low_date"] = current["low_date"]

            previous["high"] = min(ph, high)
            previous["low"] = min(pl, low)

        previous["date"] = current.get(
            "date", previous.get("date")
        )

    return result
