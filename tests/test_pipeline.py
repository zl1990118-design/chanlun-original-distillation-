import unittest
from src.pipeline import analyze_bars


class TestCandidatePipeline(unittest.TestCase):
    def test_inclusion_then_top_fractal(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {"date": "2026-10-02", "high": 12, "low": 7},
            {"date": "2026-10-03", "high": 11, "low": 6},
        ]

        result = analyze_bars(bars)

        self.assertEqual(result["rule_status"], "UNVERIFIED")
        self.assertEqual(result["candidate_fractals"][0]["type"], "top")

    def test_too_few_bars(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {"date": "2026-10-02", "high": 12, "low": 7},
        ]
        result = analyze_bars(bars)
        self.assertEqual(result["candidate_fractals"], [])


    def test_pipeline_preserves_fractal_index_and_extreme_date(self):
        bars = [
            {"date": "2026-10-01", "high": 10, "low": 5},
            {
                "date": "2026-10-02",
                "high": 12,
                "low": 7,
                "high_date": "2026-10-04",
            },
            {"date": "2026-10-03", "high": 11, "low": 6},
        ]

        result = analyze_bars(bars)

        self.assertEqual(len(result["merged_bars"]), 3)
        fractal = result["candidate_fractals"][0]
        self.assertEqual(fractal["type"], "top")
        self.assertEqual(fractal["index"], 1)
        self.assertEqual(fractal["date"], "2026-10-04")


if __name__ == "__main__":
    unittest.main()
