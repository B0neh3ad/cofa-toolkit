---
name: csv-order-contract
description: Review an order CSV aggregation task for status filtering, validity, duplicate identity and decimal rounding against its stated contract; use for order-summary implementation and regression review.
---

Read the task's actual order schema and policy before applying this review. Do not assume that the practice exercise's status values, identity key, or rounding rule applies to another dataset.

Trace one included, one excluded, one invalid, and one duplicate order through the actual code. Check whether normalization and validity occur before identity is reserved, according to the stated policy. Check missing headers separately from a valid empty dataset.

For money, identify where decimal conversion, per-order or aggregate rounding, and output formatting occur. Check nonfinite values and a rounding-boundary example. Confirm expected totals independently from the implementation.

Test invariants relevant to the contract, such as adding an excluded order leaving totals unchanged, or adding a duplicate valid order leaving totals unchanged under a first-valid-order policy. Do not use row-order invariance when first-valid-order selection makes row order significant.

In the bundled practice task, use PRACTICE.txt and checks.json. Existing tests intentionally leave room to find missing coverage. Inspect BOM/header handling, whitespace normalization, error behavior and the actual sample CLI, rather than reporting only the current test count. Use the evidence harness if useful, preserve an actual failing regression before a fix, and report file/function, input, observed result, expected result and check run.
