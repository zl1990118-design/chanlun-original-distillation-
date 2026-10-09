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


    def test_top_uses_high_date(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {
                "date": "2026-10-02",
                "high": 13,
                "low": 7,
                "high_date": "2026-10-04",
            },
            {"date": "2026-10-03", "high": 11, "low": 6},
        ]

        result = identify_fractals(bars)
        self.assertEqual(result[0]["type"], "top")
        self.assertEqual(result[0]["date"], "2026-10-04")
        self.assertEqual(result[0]["price"], 13)

    def test_bottom_uses_low_date(self):
        bars = [
            {"date": "2026-10-01", "high": 13, "low": 8},
            {
                "date": "2026-10-02",
                "high": 10,
                "low": 4,
                "low_date": "2026-10-05",
            },
            {"date": "2026-10-03", "high": 12, "low": 6},
        ]

        result = identify_fractals(bars)
        self.assertEqual(result[0]["type"], "bottom")
        self.assertEqual(result[0]["date"], "2026-10-05")
        self.assertEqual(result[0]["price"], 4)


if __name__ == "__main__":
    unittest.main()
