---
name: session-handoff
description: Write or reconcile a compact handoff at a verified checkpoint so a new agent session can resume the same task without reconstructing the prior conversation.
---

Update the existing work log instead of duplicating it. Record the current goal and fixed constraints, code state, last relevant verification and evidence location, unresolved decisions, and next executable action. Distinguish verified behavior from pending work.

If parallel work is active, include each task's directory, branch, latest completed commit, checks, integration status, and dependencies. Do not imply that uncommitted files or ignored setup will appear in another checkout. Identify running processes and resource ownership when relevant; do not stop them merely to write a handoff.

Prefer a completed, tested task boundary. If interruption occurs during a merge, command, or partial edit, describe that state and the safe next action explicitly. Exclude secret values and unnecessary raw logs.

When resuming, compare the note with actual files and task state. Run the smallest relevant check when needed, mark stale evidence, then continue authorized work. Keep historical narrative out of the operational handoff. This supports permitted development, not AI assistance during a prohibited assessment stage.
