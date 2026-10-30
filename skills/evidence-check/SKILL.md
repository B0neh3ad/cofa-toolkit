---
name: evidence-check
description: Check an implementation or analysis against explicit acceptance criteria and return execution evidence when the user requests verification or a final delivery review.
---

Match each mandatory criterion to the smallest useful check. Inspect the implementation and existing project checks before choosing commands. Preserve the task's required interfaces and environment restrictions.

Run appropriate checks and distinguish observed results from assumptions. For each material result, report the input, expected behavior, actual behavior, command or manual procedure, and relevant file location. State failures and checks that could not run. Do not invent an exit code or treat a subagent's claim as execution evidence.

Tie material claims to the tested code state, using a commit plus working-tree state or relevant file hashes. Preserve a reproducing failing check for a real defect, then rerun the same check after fixing it. If the fixture, test, or expected result changes, obtain a new baseline before claiming a same-check failure-to-pass transition. Do not fabricate a defect or history to produce evidence.

Distinguish unit, mock, local integration, actual external integration, and manual checks. A runner's category label does not establish that an external call occurred. Use only infrastructure and credentials permitted by the task. Identify the untested boundary when real integration is unavailable.

If scripts/run_checks.py is present in the selected toolkit, inspect the project's configuration before running it. Its source hashes cover only declared paths, its log redaction is incomplete, and its status transitions still require cause review. Use the project's existing harness instead when it already provides adequate evidence.

Prioritize the main user flow, a relevant failure case, and risks introduced by the changes. For data work, check the domain's conservation or consistency rule when applicable. Avoid adding tests that only repeat implementation details.

If the user requested a read-only review, report findings without editing. Rank actionable findings by impact and give a reproducing example. If no issue is established, say what was checked and what remains uncertain.

Use the project's required output format. Do not create extra reports unless they help the requested delivery.
