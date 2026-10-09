import unittest
from src.fractals import identify_fractals


class TestCandidateFractals(unittest.TestCase):
    def test_top(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {"date": "2026-10-02", "high": 13, "low": 7},
            {"date": "2026-10-03", "high": 11, "low": 6},
        ]
        self.assertEqual(identify_fractals(bars)[0]["type"], "top")

    def test_bottom(self):
        bars = [
            {"date": "2026-10-01", "high": 13, "low": 8},
            {"date": "2026-10-02", "high": 10, "low": 4},
            {"date": "2026-10-03", "high": 12, "low": 6},
        ]
        self.assertEqual(identify_fractals(bars)[0]["type"], "bottom")

    def test_equal_high_is_not_top(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {"date": "2026-10-02", "high": 12, "low": 7},
            {"date": "2026-10-03", "high": 12, "low": 6},
        ]
        self.assertEqual(identify_fractals(bars), [])

    def test_too_few_bars(self):
        self.assertEqual(identify_fractals([]), [])
        self.assertEqual(identify_fractals([{"high": 1, "low": 0}]), [])


if __name__ == "__main__":
    unittest.main()
