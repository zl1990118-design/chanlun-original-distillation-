def merge_inclusions(bars):
    """合并相邻包含K线的候选实现；规则仍需按原文核验。"""
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

        if len(result) >= 2:
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
                direction = "unknown"
        else:
            direction = "unknown"

        if direction == "up":
            previous["high"] = max(ph, high)
            previous["low"] = max(pl, low)
        elif direction == "down":
            previous["high"] = min(ph, high)
            previous["low"] = min(pl, low)
        else:
            previous["high"] = max(ph, high)
            previous["low"] = min(pl, low)

        previous["date"] = current.get(
            "date", previous.get("date")
        )

    return result
