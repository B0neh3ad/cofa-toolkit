"""Acceptance checks; failures are expected before repairing the starter."""

import csv
import tempfile
import unittest
from pathlib import Path

from orders import summarize


class OrderSummaryTests(unittest.TestCase):
    def run_rows(self, rows):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["order_id", "team", "quantity", "unit_price", "status"])
                writer.writerows(rows)
            return summarize(path)

    def test_normal_and_empty(self):
        self.assertEqual(self.run_rows([]), {})
        self.assertEqual(self.run_rows([
            ["a", "alpha", "2", "10.00", "completed"],
            ["b", "beta", "3", "7.50", "completed"],
        ]), {"alpha": "20.00", "beta": "22.50"})

    def test_cancelled_orders_do_not_contribute(self):
        self.assertEqual(self.run_rows([
            ["a", "alpha", "2", "10.00", "completed"],
            ["b", "alpha", "1", "99.00", "cancelled"],
        ]), {"alpha": "20.00"})

    def test_first_valid_order_id_wins(self):
        self.assertEqual(self.run_rows([
            ["a", "alpha", "1", "5.00", "completed"],
            ["a", "alpha", "3", "5.00", "completed"],
        ]), {"alpha": "5.00"})

    def test_invalid_rows_do_not_contribute_or_claim_ids(self):
        self.assertEqual(self.run_rows([
            ["a", "alpha", "-1", "5.00", "completed"],
            ["a", "alpha", "1", "5.00", "completed"],
            ["b", "alpha", "1", "NaN", "completed"],
            ["c", "", "1", "5.00", "completed"],
            ["d", "alpha", "1", "5.00", "pending"],
            ["e", "alpha", "1.5", "5.00", "completed"],
            ["f", "alpha", "1", "Infinity", "completed"],
            ["g", "alpha", "0", "5.00", "completed"],
            ["h", "alpha", "1", "-5.00", "completed"],
            ["", "alpha", "1", "5.00", "completed"],
        ]), {"alpha": "5.00"})

    def test_decimal_rounding_is_per_order_half_up(self):
        self.assertEqual(self.run_rows([
            ["a", "alpha", "1", "1.005", "completed"],
            ["b", "alpha", "1", "1.005", "completed"],
        ]), {"alpha": "2.02"})


if __name__ == "__main__":
    unittest.main()
