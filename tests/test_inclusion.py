import unittest
from src.inclusion import merge_inclusions


class TestCandidateInclusionMerge(unittest.TestCase):
    def test_no_inclusion_keeps_bars(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {"date": "2026-10-02", "high": 12, "low": 7},
        ]
        result = merge_inclusions(bars)
        self.assertEqual(len(result), 2)

    def test_up_direction_tracks_extrema_dates(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {"date": "2026-10-02", "high": 12, "low": 7},
            {"date": "2026-10-03", "high": 11, "low": 8},
        ]
        result = merge_inclusions(bars)
        merged = result[-1]

        self.assertEqual(len(result), 2)
        self.assertEqual(merged["high"], 12)
        self.assertEqual(merged["low"], 8)
        self.assertEqual(merged["high_date"], "2026-10-02")
        self.assertEqual(merged["low_date"], "2026-10-03")

    def test_down_direction_tracks_extrema_dates(self):
        bars = [
            {"date": "2026-10-01", "high": 12, "low": 8},
            {"date": "2026-10-02", "high": 10, "low": 6},
            {"date": "2026-10-03", "high": 9, "low": 7},
        ]
        result = merge_inclusions(bars)
        merged = result[-1]

        self.assertEqual(len(result), 2)
        self.assertEqual(merged["high"], 9)
        self.assertEqual(merged["low"], 6)
        self.assertEqual(merged["high_date"], "2026-10-03")
        self.assertEqual(merged["low_date"], "2026-10-02")

    def test_invalid_range_raises(self):
        bars = [{"date": "2026-10-01", "high": 5, "low": 8}]
        with self.assertRaises(ValueError):
            merge_inclusions(bars)

    def test_missing_field_raises(self):
        bars = [{"date": "2026-10-01", "high": 10}]
        with self.assertRaises(ValueError):
            merge_inclusions(bars)

    def test_equal_range_without_direction_raises(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {"date": "2026-10-02", "high": 10, "low": 5},
        ]
        with self.assertRaisesRegex(ValueError, "无法确定包含合并方向"):
            merge_inclusions(bars)

    def test_inclusion_chain_keeps_valid_range(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {"date": "2026-10-02", "high": 12, "low": 7},
            {"date": "2026-10-03", "high": 11, "low": 8},
        ]
        result = merge_inclusions(bars)

        for bar in result:
            self.assertLessEqual(bar["low"], bar["high"])


if __name__ == "__main__":
    unittest.main()
