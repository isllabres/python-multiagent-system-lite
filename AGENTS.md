# AGENTS.md — working contract

Instructions for OpenCode in this repository. This file is the map and the hard rules; the
detail lives in the roles (`.opencode/agent/`) and the skills (`.opencode/skills/`), read when
they are needed.

## The idea

A change can pass every test and still be the wrong change, or be written so badly that the next
one breaks it. Three specialised agents catch that difference: a manager who decides scope, an
implementer who builds test-first, and a reviewer who judges the result against both the
person's original request and a shared Python rubric — each with one job, never the others'.

## A layer, not a project template

This system creates no `src/`, `tests/`, or any directory of your project; it adapts to the
project at hand. The only things an agent writes on its own are `.opencode/commit-style.md`
(learned once, on first use) and, of course, whatever source and test files the implementer is
asked to build. Separately — no agent judgment involved, a plain script — `/log-usage` appends
this deployment's own OpenCode cost and token usage to `.opencode/token-usage.jsonl`, local and
git-ignored; see "Token usage, logged locally" below.

## The map — read what you need, when you need it

| What | Holds | Read it |
|---|---|---|
| `AGENTS.md` | The contract | Always |
| `.opencode/commands/initial-setup.md` | The `/initial-setup` command | Once, right after installing the layer |
| `.opencode/commands/log-usage.md` | The `/log-usage` command | Whenever you want this deployment's usage log updated |
| `.opencode/agent/*.md` | The three agents | When you delegate to one |
| `.opencode/skills/tdd/` | Red/green/refactor, commit rules, the first-run commit-style bootstrap | Before implementing or reviewing |
| `.opencode/skills/python-standards/` | The Python rubric | Before writing or reviewing code |
| `.opencode/skills/grill-me/`, `create-issue/`, `implement-issue/`, `update-issue/` | The optional GitHub-issue workflow | Only when the manager decides one is warranted, and only after asking you |
| `.opencode/commit-style.md` | This repository's own commit convention, learned on first use | Before every commit |
| `.opencode/scripts/log_usage.py` | The usage logger `/log-usage` runs | Never read directly — run it |
| `.opencode/token-usage.jsonl` | This deployment's own cost/token history, local and git-ignored | For comparing usage across changes to this layer |

## The loop

```
request ──▶ manager lists behaviours ──▶ implementer builds test-first ──▶ reviewer judges
                                                     ▲                           │
                                                     └──── up to 3 rounds ───────┘
                                                                                  ▼
                                                                    manager reports back to you
```

No gate beyond the conversation itself: nothing is filed, branched by convention, or opened as a
pull request automatically. The implementer commits as it goes; what you do with the result
(open a PR, merge it, discard it) is yours to decide. The optional `create-issue` /
`implement-issue` / `update-issue` skills run this same loop anchored to a GitHub issue, ending
in a local PR you confirm — but the manager only reaches for them after asking you, never as
the default path.

## Three agents, each with one job

| Agent | Mode | Writes | Never |
|---|---|---|---|
| `manager` | primary | Nothing — delegates and reports back | Code, tests, review verdicts |
| `implementer` | subagent | Tests, code, commits, `.opencode/commit-style.md` on first use | Scope decisions, review verdicts |
| `reviewer` | subagent | Its verdict and findings, relayed by the manager | Code, tests, commits |

Model and permissions are per-agent (`.opencode/agent/*.md`, each a plain `provider/model-id` in
its frontmatter — add one, or leave it unset to use OpenCode's configured default) and
per-project (`.opencode/opencode.json`). This layer ships sane defaults, not a fixed provider or
a fixed toolchain.

## First run in a new repository

The implementer has no opinion of its own about commit messages. Before its first commit here,
it reads the existing `git log` and writes what it finds to `.opencode/commit-style.md`, then
follows that file for every commit after, in this and future sessions. A repository with no
usable history yet falls back to plain Conventional Commits. The exact procedure is in the
`tdd` skill.

Run `/initial-setup` once, right after installing the layer, to do this same learning up front
and thoroughly — the complete history instead of a quick sample — and to get back a report on
this repository's toolchain and working conventions before the first real request. It is
optional: skipping it just means the implementer learns the same thing lazily, from a smaller
sample, before its first commit.

## Token usage, logged locally

Run `/log-usage` (or `python .opencode/scripts/log_usage.py` directly) whenever you want this
deployment's own OpenCode session history folded into `.opencode/token-usage.jsonl` — one line
per session, cost and token counts read straight from `opencode session export`, nothing
estimated or self-reported by a model. It exists to compare *this* deployment's spend over
time — before and after a model swap, a cheaper default per agent, a caching change — never to
feed a model's own judgment about cost. Local and git-ignored: it never leaves this machine and
never shows up as a diff. `session list` only surfaces top-level sessions, so a subagent's own
child session may be missing from the totals; `--session-id` logs one by hand as a fallback.

## States, deduced and never stored

A request exists only for the length of the conversation that handles it: nothing is tracked as
draft, open, or in review anywhere outside that conversation. What persists across sessions is
the code itself, its commit history, and `.opencode/commit-style.md`.
