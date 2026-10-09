import unittest

from src.market_data import validate_daily_bar


class TestDailyBar(unittest.TestCase):
    def setUp(self):
        self.bar = {
            "date": "2026-10-09",
            "open": 10,
            "high": 12,
            "low": 9,
            "close": 11,
        }

    def test_valid_bar(self):
        self.assertTrue(validate_daily_bar(self.bar))

    def test_high_below_close(self):
        self.bar["high"] = 10.5
        with self.assertRaises(ValueError):
            validate_daily_bar(self.bar)

    def test_missing_field(self):
        del self.bar["close"]
        with self.assertRaises(ValueError):
            validate_daily_bar(self.bar)

    def test_invalid_date(self):
        self.bar["date"] = "not-a-date"
        with self.assertRaises(ValueError):
            validate_daily_bar(self.bar)


if __name__ == "__main__":
    unittest.main()
