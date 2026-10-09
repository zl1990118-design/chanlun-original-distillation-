"""候选分析流程；规则尚待缠论原文核验。"""
from src.inclusion import merge_inclusions
from src.fractals import identify_fractals


def analyze_bars(bars):
    """先处理包含关系，再识别候选分型。"""
    merged = merge_inclusions(bars)
    fractals = identify_fractals(merged)

    return {
        "rule_status": "UNVERIFIED",
        "merged_bars": merged,
        "candidate_fractals": fractals,
    }
