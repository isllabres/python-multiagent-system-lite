# python-multiagent-system-lite

A minimal multi-agent system for Python development, for [OpenCode](https://opencode.ai). It
drops onto a Python project that has already started and runs a manager → implementer →
reviewer orchestration: the manager turns a request into a short list of behaviours, the implementer
builds each one test-first, and the reviewer judges the result before it's called done.

```
you describe a task ──▶ manager lists behaviours ──▶ implementer builds test-first
                                                                │
                                              ◀── reviewer judges the diff (≤3 rounds)
                                             manager reports back to you
```

By default: no specs, no GitHub issues, no pull requests, no wiki. The manager talks to you
directly, in the conversation, and reports back the same way. Five optional skills
(`grill-me`, `create-issue`, `implement-issue`, `update-issue`, `propose-upstream`) add a plain
GitHub-issue-and-PR flow on top of the same three roles, for a request that's worth tracking or
interrogating before anyone builds it — the manager only reaches for one after asking you, never
on its own. This repository is the one source of truth for the layer itself: `/update-layer`
pulls a newer tagged release into a project that installed it, and `propose-upstream` sends an
idea about the layer back here as an issue — see "Staying up to date" below. If you outgrow even
that,
[python-multiagent-system](https://github.com/isllabres/python-multiagent-system) adds
spec-driven (OpenSpec) changes and a generated wiki on top of the same idea.

## Install into an existing project

Requirements: [OpenCode](https://opencode.ai), `git`. No particular Python toolchain is assumed
— the agents detect whatever the project already uses (`uv`, `poetry`, plain `pip`; `ruff` or
`flake8`/`black`; `mypy` or `pyright`; `pytest` or `unittest`) rather than hardcoding one.

```bash
# 1. Get the layer, once
git clone https://github.com/isllabres/python-multiagent-system-lite.git ~/code/python-multiagent-system-lite

# 2. Export a clean snapshot into your project (tracked files only)
git -C ~/code/python-multiagent-system-lite archive HEAD .opencode AGENTS.md \
  | tar -x -C ~/code/my-project

# 3. Sign in to whichever provider(s) your agents will use
cd ~/code/my-project
opencode providers login          # e.g. Anthropic, or set ANTHROPIC_API_KEY

# 4. Commit the layer to your project's own repository
git switch -c add-multiagent-layer
git add .opencode AGENTS.md
git commit -m "Add the python-multiagent-system-lite layer"

# 5. Start working
opencode
```

Once inside, run `/initial-setup` before your first real request. It reads this project's
complete git history and source layout, derives `.opencode/commit-style.md` from it (see "First
run" below), and reports back the toolchain and conventions it found — the one-time pass that
lets every agent after it be compliant with this specific project instead of guessing. It's
optional — skip it and the implementer learns the same thing lazily, from a smaller sample,
before its first commit — but worth the one run.

`git archive` is used instead of `cp -r` because it copies only tracked files, so no
`.DS_Store` or local cache comes along. Plain `opencode` already starts you as `manager` — the
layer's `.opencode/opencode.json` sets `default_agent: "manager"` — so there's no flag to
remember.

### Before you start

- **An existing `AGENTS.md` is overwritten by step 2.** If you already have one, export only
  `.opencode`, put this one beside yours under another name, and import it with a plain
  `@path` reference (OpenCode resolves it relative to the file that mentions it, the same
  convention Claude Code uses):

  ```bash
  git -C ~/code/python-multiagent-system-lite archive HEAD .opencode | tar -x -C ~/code/my-project
  git -C ~/code/python-multiagent-system-lite archive HEAD AGENTS.md | tar -xO \
    > ~/code/my-project/AGENTS.multiagent.md
  ```

  then add `@AGENTS.multiagent.md` to your own `AGENTS.md`.
- **An existing `.opencode/opencode.json` is merged by hand, not overwritten.** Fold its
  `permission.bash` block into yours; without it, the commands this layer needs will prompt for
  approval every time instead of running straight through.
- **Set a model per agent, or don't.** Each `.opencode/agent/*.md` has a frontmatter you can add
  a `model: provider/model-id` line to. Left unset, OpenCode uses its configured default — mix
  providers per agent once you hold credentials for each; `opencode models <provider>` lists
  what's available. All three do real judgment (scoping, building, reviewing against
  `python-standards`), so there's no mechanically "cheap" role to downgrade by default — but the
  reviewer's tooling pass (running the project's actual test/lint/type-check commands) is the
  most mechanical part of any of the three, and the likeliest place a cheaper model still holds
  up. Run `/log-usage` for a few requests before and after a swap to see whether it actually did.
- **Almost everything here is plain Markdown** — nothing to exclude from your linter or test
  discovery — except `.opencode/scripts/log_usage.py`, a small stdlib-only script behind
  `/log-usage`; exclude that one path if your linter would otherwise lint this layer's own
  tooling as part of your project.

## First run in a repository: learning your commit style

This layer has no house commit convention of its own. Run `/initial-setup` once to learn it up
front, from the complete history; skip it and the implementer learns the same thing lazily,
from a 30-commit sample, before its very first commit instead of guessing:

1. **Checks for `.opencode/commit-style.md`.** If it's already there (a previous session wrote
   it), it just reads and follows it — nothing below happens again.
2. **Otherwise, reads your history**: `git log --format='%s%n%b%n---' -30` for the subjects and
   bodies, plus `git log --oneline -30` to catch anything a branch name echoes into them.
3. **Works out the pattern** actually in use, not a rubric imposed on it:
   - subject style — length, case, mood (imperative vs. past tense), a `type:`/`type(scope):`
     prefix, a ticket ID in brackets or a trailing footer, an emoji;
   - whether a body is used, and for what (the "why", a `Review:`/footer line, issue
     references);
   - whether a ticket ID or type comes from the branch name and gets echoed into commits.
4. **Writes it down** as a short rubric plus one real example lifted from the log, to
   `.opencode/commit-style.md` — something like:

   ```markdown
   # Commit style (learned from this repository's history)

   - Subject: imperative, lower-case start, under 72 characters, no trailing period.
   - Prefix: none observed — plain subjects, no `type:` tag, no ticket ID.
   - Body: used occasionally for the "why"; no footer convention observed.
   - Example: "stop retrying 5xx responses after the third attempt"
   ```

5. **Commits that file itself**, in the convention it just derived — the one exception to
   "write the test before the code," since this is tooling, not a behaviour. A repository with
   fewer than five commits to learn from skips steps 2–4 and bootstraps with plain
   [Conventional Commits](https://www.conventionalcommits.org/) instead (`type: subject`,
   imperative, under 72 characters), noting that in the file.

Every commit after — by the implementer, in this session or a later one — follows
`.opencode/commit-style.md`, never a fresh guess. If your convention changes, or you just want
it re-derived, delete that file and the next commit re-learns it. The exact rule lives in the
`tdd` skill, next to the red/green/refactor cycle it also governs.

## The three agents

| Agent | Mode | Owns | Never |
|---|---|---|---|
| `manager` | primary | Turning the request into behaviours, delegating, relaying review rounds (capped by blast radius, ≤3), reporting back | Code, tests, judging code |
| `implementer` | subagent | Tests first, then the code, one behaviour at a time; every commit | Scope decisions, review verdicts |
| `reviewer` | subagent | Judging the diff against the person's original request and `python-standards`, an `APPROVED`/`CHANGES_REQUESTED` verdict | Code, tests, commits |

See `.opencode/agent/*.md` for each one's full instructions, and `AGENTS.md` for the contract
they all share.

## Commands

- **`/initial-setup`** — run once, right after install: learns `.opencode/commit-style.md` from
  the complete history instead of the lazy 30-commit sample, and reports the toolchain and
  working conventions this layer found. See `.opencode/commands/initial-setup.md`.
- **`/log-usage`** — updates a local, git-ignored `.opencode/token-usage.jsonl` with this
  deployment's own OpenCode session cost and token counts (via `opencode session export`,
  nothing self-reported by a model), then prints running totals by agent and model — so you can
  compare spend before and after a model swap, a cheaper default, or a caching change. See
  `.opencode/commands/log-usage.md` and `.opencode/scripts/log_usage.py`.
- **`/update-layer`** — checks the repo named in `.opencode/layer.json` for a newer tagged
  release and, if there is one, pulls `.opencode/` and `AGENTS.md` from it. Nothing is
  committed; the result is a plain diff to review. See `.opencode/commands/update-layer.md` and
  `.opencode/scripts/update_layer.py`.

## Skills

- **`tdd`** — the red/green/refactor cycle, commit granularity, and the first-run commit-style
  bootstrap described above. Always in play.
- **`python-standards`** — the shared rubric for good Python: the implementer writes to it, the
  reviewer checks the diff against it. The project's own conventions always win over the
  rubric. Always in play.
- **`grill-me`** *(optional)* — one question at a time, each with a recommendation, until every
  decision a thin or risky idea depends on is pinned down. The manager performs this itself.
- **`create-issue`** *(optional)* — turns an idea into a GitHub issue: a summary, a behaviour
  checklist, what's out of scope, what's still open. You approve the issue before it's filed.
- **`implement-issue`** *(optional)* — runs the normal manager → implementer → reviewer loop
  anchored to an existing issue's checklist, ticking it off as it goes, and ends at a local PR
  you confirm before anything is pushed.
- **`update-issue`** *(optional)* — changes a filed issue's checklist or description, with the
  difference shown to you before it's edited.
- **`propose-upstream`** *(optional)* — turns an idea about this layer itself (not the project
  it's installed in) into an issue filed against the repo named in `.opencode/layer.json`, so a
  fix found in one project can reach every project using this layer.

The five optional ones need `git` and `gh` (GitHub CLI, authenticated); nothing else in this
layer does. The manager never loads one without telling you first and getting a go-ahead — see
"Optional workflows" in `.opencode/agent/manager.md`.

## Staying up to date, and sending improvements back

This repository is the one place this layer's own definition lives. Every project that
installed it is a snapshot of some tagged release, recorded in `.opencode/layer.json`
(`{"repo": "...", "version": "v0.1.0"}`) — written the moment you install, and kept current by
`/update-layer` after that.

- **Pulling an update** — run `/update-layer`. It lists the tags on the repo named in
  `layer.json` with a plain `git ls-remote` (no clone, no auth needed for a public repo), and if
  a newer one exists, downloads that tag's public GitHub archive and overwrites `.opencode/` and
  `AGENTS.md` with it. `.opencode/commit-style.md` and `.opencode/token-usage.jsonl` are never
  touched — they're this project's own state, not part of the layer. Nothing is committed for
  you; review the result like any other change, especially `.opencode/opencode.json` if you've
  customized its permissions, since an update overwrites it wholesale.
- **Sending an idea back** — when something found in one project is really about the layer
  itself rather than that project's own code, the manager can offer `propose-upstream`: the same
  discovery-then-approve shape `create-issue` already uses, aimed at the repo named in
  `layer.json` instead of the project at hand, so the fix reaches every project using this
  layer, not just this one.

Cutting a release, from this repository's own side, is a plain `git tag vX.Y.Z && git push
--tags` (or `gh release create vX.Y.Z`) once `main` is where you want it — nothing here needs
CI, a build step, or anything beyond the tag itself.

## Scope

By default, no issue tracker integration, no PR automation, no generated documentation: the
manager reports back in the conversation and nothing is filed anywhere. The five optional
skills above add a GitHub issue/PR flow on top, one request at a time, only with your
go-ahead — never silently, never by default. Review rounds are capped either way — up to three
for anything with real blast radius, fewer for a small, reversible change, sized the same way
`grill-me` sizes its own depth — and the manager stops and asks you the moment a round repeats
what the last one already said, not just once the ceiling is hit.

## Reliability patterns this layer follows

Checked against two Anthropic pieces on building agent automations that actually hold
up — [Claude Managed Agents](https://claude.com/resources/articles/claude-managed-agents) and
[Building effective agent automations](https://claude.dev/blog/building-effective-agent-automations/).
Most of the first one's platform machinery (vaults, managed cloud sandboxes, cron deployments,
"dreaming") doesn't transfer to a local, markdown-defined layer. What does transfer, from both
pieces, is the list below — some of it was already how this layer worked, the rest (untrusted
content as data, visible read failures, per-behaviour done-criteria, confirmed commits) was
added once these two pieces named the gap:

- **One orchestrator, no peer-to-peer agents.** The implementer and reviewer never talk to each
  other directly (`task: deny` on both); every handoff goes through the manager, the only agent
  the person talks to. No coordination explosion, no agent improvising a message to another
  behind your back.
- **Grounded verification, not self-report.** The reviewer re-runs the project's actual test,
  lint and type-check commands itself rather than trusting the implementer's claim that they
  pass — the same "re-verify against the live source before acting" principle a long-running
  agent needs for anything it reports as true.
- **Bounded, blast-radius-sized rounds.** Review rounds escalate to the person the moment one
  repeats what the last one said, and the ceiling itself scales with how risky the change is
  (`grill-me`'s own heuristic) — not a flat retry count treating a one-line fix and a public
  interface the same way.
- **Human confirmation before the expensive part.** The manager shows its behaviour list before
  delegating; a yes, a tweak, or silence is enough, but nothing gets built on a guess about scope
  nobody confirmed.
- **A stated done-criterion per behaviour**, not just a one-sentence label — handed to the
  reviewer alongside the request, so "does this meet what was asked" has something concrete to
  check per behaviour instead of a judgment call reconstructed from a label.
- **Untrusted content is data, not instructions** (`AGENTS.md`, all three agents) — a comment,
  commit message, or issue body trying to steer a verdict or scope is a finding, never a command
  followed.
- **Least-privilege per role.** Permissions are scoped in each agent's own frontmatter
  (`task: deny` for implementer and reviewer, `webfetch`/`websearch` only where a role needs
  them), not one shared, maximal permission set.
- **A commit only counts as done once it's confirmed landed** (`tdd` skill) — `git log -1` /
  `git status`, not just the tool call returning without an error, since a rejected pre-commit
  hook can look like success from the implementer's own side.
- **A bookmark, not a fixed window.** `/log-usage` dedupes by session id already logged, so
  re-running it never double-counts or needs a time range to stay correct.
- **A failed read is never silent** (`.opencode/scripts/log_usage.py`) — a session the logger
  couldn't export now shows up in its summary as "N session(s) could not be read," not as a run
  indistinguishable from a quiet one.
- **Short output on purpose.** Findings are capped at a few real ones ("three real findings beat
  thirty nitpicks"), and reports stay to a line or two — what changes a decision, not everything
  that happened.
