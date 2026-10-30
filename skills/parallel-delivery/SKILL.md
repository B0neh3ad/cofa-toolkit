---
name: parallel-delivery
description: Plan and coordinate deadline-bound parallel implementation with explicit dependencies, file ownership, and optional Git worktree isolation when parallel delivery is requested.
---

Keep reusable rules in project guidance and variable task facts in the current work log. Identify the smallest interface contract and each task's prerequisites, owned files, completion check, and shared resources. Avoid a separate document when a short existing table is enough.

Start ready independent work without waiting for unrelated tasks. Use the available agent controls only when delegation is authorized. Prefer at most two writing workers initially, subject to actual limits and setup cost. A separate agent context does not establish a separate checkout; verify each worker's directory, branch, and baseline. If worktree creation is unavailable or uneconomical, use one writer with bounded read-only investigation or review.

One coordinator owns integration, shared configuration, dependency manifests, lockfiles, and common status records. Workers commit only assigned files and return the commit, check result, remaining risk, and downstream dependency. Review a stable snapshot when writers are still active.

Collect completed tasks as they finish. Integrate reviewed commits serially in the designated submission checkout, then run relevant checks on that combined state. Worker-local success does not establish integrated success. Never leave required work only in an auxiliary checkout.

Reserve time for integration and the user's explanation of why, where, evidence, and limits. Reduce parallelism when shared files, resources, or late contract changes dominate. Follow existing permissions and assessment restrictions; do not modify managed settings or create external publication as part of this workflow.

Use only the Git worktree behavior actually supported by the host. Committed baselines, ignored setup, ports and databases require separate coordination; do not assume a new checkout copies them.
