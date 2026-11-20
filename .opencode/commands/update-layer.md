---
description: Checks the repo named in .opencode/layer.json for a newer tagged release and, if there is one, pulls .opencode/ and AGENTS.md from it. Nothing is committed; review the diff like any other change.
agent: manager
---

Pull a newer tagged version of this layer itself (not a project dependency - the
manager/implementer/reviewer definition this project installed), the same way `/initial-setup`
pulls this repository's own history: read-only until the last step, nothing filed or committed
on its own.

!`python3 .opencode/scripts/update_layer.py --check`

If that already says "already on ... which is the latest tag," tell the person and stop here -
there's nothing to pull.

Otherwise, run the real update:

!`python3 .opencode/scripts/update_layer.py`

Report what it printed: which version it moved from and to, how many files it wrote, and - most
important - that nothing is committed yet. Tell the person to review `git status`/`git diff`
before committing, calling out `.opencode/opencode.json` by name if it's among the changed
files and they've customized its permissions block, since an update overwrites it wholesale.

`.opencode/commit-style.md` and `.opencode/token-usage.jsonl` are never touched by this - they
were never part of the layer, they're this project's own state.
