"""Additional contract regressions found by the order-specific review."""

import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from orders import summarize


class ContractGapTests(unittest.TestCase):
    def test_whitespace_is_normalized_before_team_and_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "orders.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["order_id", "team", "quantity", "unit_price", "status"])
                writer.writerows([
                    [" a ", " alpha ", "1", "5.00", "completed"],
                    ["a", "alpha", "3", "5.00", "completed"],
                ])
            self.assertEqual(summarize(path), {"alpha": "5.00"})

    def test_missing_required_header_is_cli_error_even_without_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "orders.csv"
            path.write_text("team,quantity,unit_price,status\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("orders.py")), str(path)],
                capture_output=True, text=True, timeout=5,
            )
            self.assertNotEqual(result.returncode, 0, "Missing schema must not become a normal empty result")


if __name__ == "__main__":
    unittest.main()
