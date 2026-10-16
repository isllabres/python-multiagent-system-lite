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
directly, in the conversation, and reports back the same way. Four optional skills
(`grill-me`, `create-issue`, `implement-issue`, `update-issue`) add a plain GitHub-issue-and-PR
flow on top of the same three roles, for a request that's worth tracking or interrogating
before anyone builds it — the manager only reaches for one after asking you, never on its own.
If you outgrow even that,
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
  what's available.
- **This layer's scripts/files are plain Markdown** — nothing to exclude from your linter or
  test discovery.

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
| `manager` | primary | Turning the request into behaviours, delegating, relaying review rounds (≤3), reporting back | Code, tests, judging code |
| `implementer` | subagent | Tests first, then the code, one behaviour at a time; every commit | Scope decisions, review verdicts |
| `reviewer` | subagent | Judging the diff against the person's original request and `python-standards`, an `APPROVED`/`CHANGES_REQUESTED` verdict | Code, tests, commits |

See `.opencode/agent/*.md` for each one's full instructions, and `AGENTS.md` for the contract
they all share.

## Commands

- **`/initial-setup`** — run once, right after install: learns `.opencode/commit-style.md` from
  the complete history instead of the lazy 30-commit sample, and reports the toolchain and
  working conventions this layer found. See `.opencode/commands/initial-setup.md`.

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

The four optional ones need `git` and `gh` (GitHub CLI, authenticated); nothing else in this
layer does. The manager never loads one without telling you first and getting a go-ahead — see
"Optional workflows" in `.opencode/agent/manager.md`.

## Scope

By default, no issue tracker integration, no PR automation, no generated documentation: the
manager reports back in the conversation and nothing is filed anywhere. The four optional
skills above add a GitHub issue/PR flow on top, one request at a time, only with your
go-ahead — never silently, never by default. Three rounds of review is a hard cap either way —
past that, the manager stops and asks you instead of looping on its own judgment.
