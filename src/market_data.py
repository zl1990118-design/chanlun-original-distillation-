"""日线行情数据的基础校验。"""

from datetime import date


def validate_daily_bar(bar):
    """校验单根日线的必需字段和 OHLC 关系。"""
    required = ("date", "open", "high", "low", "close")
    missing = [key for key in required if key not in bar]
    if missing:
        raise ValueError(f"缺少字段: {', '.join(missing)}")

    try:
        date.fromisoformat(str(bar["date"]))
    except (TypeError, ValueError):
        raise ValueError("date 必须是 YYYY-MM-DD 格式")

    try:
        values = {
            key: float(bar[key])
            for key in ("open", "high", "low", "close")
        }
    except (TypeError, ValueError):
        raise ValueError("OHLC 必须是数字")

    import math
    if not all(math.isfinite(value) for value in values.values()):
        raise ValueError("OHLC 不允许 NaN 或无穷大")

    if min(values.values()) <= 0:
        raise ValueError("OHLC 必须大于 0")

    if values["high"] < max(values["open"], values["close"]):
        raise ValueError("high 不能低于 open 或 close")

    if values["low"] > min(values["open"], values["close"]):
        raise ValueError("low 不能高于 open 或 close")

    if values["high"] < values["low"]:
        raise ValueError("high 不能低于 low")

    return True
