import tempfile
import unittest
from pathlib import Path

from src.csv_loader import load_daily_csv


class TestCsvLoader(unittest.TestCase):
    def make_file(self, content):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "daily.csv"
        path.write_text(content, encoding="utf-8")
        return path

    def test_load_and_sort(self):
        path = self.make_file(
            "date,open,high,low,close\n"
            "2026-10-02,11,13,10,12\n"
            "2026-10-01,9,12,8,11\n"
        )
        bars = load_daily_csv(path)
        self.assertEqual(len(bars), 2)
        self.assertEqual(bars[0]["date"], "2026-10-01")
        self.assertIsInstance(bars[0]["close"], float)

    def test_missing_column(self):
        path = self.make_file(
            "date,open,high,low\n"
            "2026-10-01,9,12,8\n"
        )
        with self.assertRaises(ValueError):
            load_daily_csv(path)

    def test_invalid_price_range(self):
        path = self.make_file(
            "date,open,high,low,close\n"
            "2026-10-01,11,10,8,11\n"
        )
        with self.assertRaises(ValueError):
            load_daily_csv(path)


if __name__ == "__main__":
    unittest.main()
