# python-multiagent-system-lite

A minimal multi-agent system for Python development, for [OpenCode](https://opencode.ai). It
drops onto a Python project that has already started and runs a manager → implementer →
reviewer loop: the manager turns a request into a short list of behaviours, the implementer
builds each one test-first, and the reviewer judges the result before it's called done.

```
you describe a task ──▶ manager lists behaviours ──▶ implementer builds test-first
                                                                │
                                              ◀── reviewer judges the diff (≤3 rounds)
                                             manager reports back to you
```

No specs, no GitHub issues, no pull requests, no wiki. The manager talks to you directly, in the
conversation, and reports back the same way. If you outgrow this,
[python-multiagent-system](https://github.com/isllabres/python-multiagent-system) adds
spec-driven changes, GitHub issues/PRs and a generated wiki on top of the same three roles.

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

This layer has no house commit convention of its own. Before its very first commit in your
project, the implementer stops and learns yours instead of guessing:

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
| `reviewer` | subagent | Judging the diff against `python-standards`, an `APPROVED`/`CHANGES_REQUESTED` verdict | Code, tests, commits |

See `.opencode/agent/*.md` for each one's full instructions, and `AGENTS.md` for the contract
they all share.

## Skills

- **`tdd`** — the red/green/refactor cycle, commit granularity, and the first-run commit-style
  bootstrap described above.
- **`python-standards`** — the shared rubric for good Python: the implementer writes to it, the
  reviewer checks the diff against it. The project's own conventions always win over the rubric.

## Scope

This is the pared-down version on purpose: no issue tracker integration, no PR automation, no
generated documentation. The manager reports back in the conversation; nothing is filed
anywhere. Three rounds of review is a hard cap — past that, the manager stops and asks you
instead of looping on its own judgment.
