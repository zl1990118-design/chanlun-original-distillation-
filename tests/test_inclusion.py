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

    def test_up_direction_candidate(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {"date": "2026-10-02", "high": 12, "low": 7},
            {"date": "2026-10-03", "high": 11, "low": 8},
        ]
        result = merge_inclusions(bars)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[-1]["high"], 12)
        self.assertEqual(result[-1]["low"], 8)

    def test_down_direction_candidate(self):
        bars = [
            {"date": "2026-10-01", "high": 12, "low": 8},
            {"date": "2026-10-02", "high": 10, "low": 6},
            {"date": "2026-10-03", "high": 9, "low": 7},
        ]
        result = merge_inclusions(bars)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[-1]["high"], 9)
        self.assertEqual(result[-1]["low"], 6)

    def test_invalid_range_raises(self):
        bars = [{"date": "2026-10-01", "high": 5, "low": 8}]
        with self.assertRaises(ValueError):
            merge_inclusions(bars)

    def test_missing_field_raises(self):
        bars = [{"date": "2026-10-01", "high": 10}]
        with self.assertRaises(ValueError):
            merge_inclusions(bars)


if __name__ == "__main__":
    unittest.main()

    def test_inclusion_equal_range_is_merged(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {"date": "2026-10-02", "high": 10, "low": 5},
        ]
        result = merge_inclusions(bars)
        self.assertEqual(len(result), 1)

    def test_inclusion_chain_keeps_valid_range(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {"date": "2026-10-02", "high": 12, "low": 7},
            {"date": "2026-10-03", "high": 11, "low": 8},
        ]
        result = merge_inclusions(bars)
        for bar in result:
            self.assertLessEqual(bar["low"], bar["high"])
