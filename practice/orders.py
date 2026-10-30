"""Intentionally faulty starter for the practice task. See PRACTICE.txt."""

import argparse
import csv
import json


def summarize(path):
    totals = {}
    with open(path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            team = row["team"]
            amount = int(row["quantity"]) * float(row["unit_price"])
            totals[team] = totals.get(team, 0.0) + amount
    return {team: f"{value:.2f}" for team, value in sorted(totals.items())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    print(json.dumps(summarize(args.path), ensure_ascii=False, sort_keys=True))
