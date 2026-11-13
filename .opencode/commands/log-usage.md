---
description: Updates the local .opencode/token-usage.jsonl with any new sessions since the last run, then shows running totals by agent and model. Local to this deployment only; nothing is sent anywhere, nothing is committed.
agent: manager
---

Pull this project's own OpenCode session history (`.opencode/scripts/log_usage.py`, which just
shells out to `opencode session list` / `session export` — nothing tracked independently of
what OpenCode already records) into a local, append-only log, so the person can compare cost
and token usage over time: before and after a model swap, a cheaper default, a caching change,
or any other tuning to this layer.

!`python3 .opencode/scripts/log_usage.py`

!`python3 .opencode/scripts/log_usage.py --summary`

Report both outputs above to the person as-is: what got logged just now (if anything — a quiet
run with nothing new to log is normal, not an error), and the running totals by agent and model.
Nothing else is written. `.opencode/token-usage.jsonl` is this machine's own file — it's
git-ignored and never committed, so it won't show up as a diff and won't follow the repository
to another clone.

If the totals look incomplete — a round you know involved the implementer or reviewer is
missing from the "agent(s)" column — say so plainly rather than presenting the numbers as
complete: `session list` only returns top-level sessions, and a subagent's own child session
may not be one of them. `.opencode/scripts/log_usage.py --session-id <id>` logs a specific
session id by hand as a fallback.
