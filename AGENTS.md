# AGENTS.md — working contract

Instructions for OpenCode in this repository. This file is the map and the hard rules; the
detail lives in the roles (`.opencode/agent/`) and the skills (`.opencode/skills/`), read when
they are needed.

## The idea

A change can pass every test and still be the wrong change, or be written so badly that the next
one breaks it. Three specialised agents catch that difference: a manager who decides scope, an
implementer who builds test-first, and a reviewer who judges the result against a shared Python
rubric — each with one job, never the others'.

## A layer, not a project template

This system creates no `src/`, `tests/`, or any directory of your project; it adapts to the
project at hand. The only things it writes on its own are `.opencode/commit-style.md` (learned
once, on first use) and, of course, whatever source and test files the implementer is asked to
build.

## The map — read what you need, when you need it

| What | Holds | Read it |
|---|---|---|
| `AGENTS.md` | The contract | Always |
| `.opencode/agent/*.md` | The three agents | When you delegate to one |
| `.opencode/skills/tdd/` | Red/green/refactor, commit rules, the first-run commit-style bootstrap | Before implementing or reviewing |
| `.opencode/skills/python-standards/` | The Python rubric | Before writing or reviewing code |
| `.opencode/skills/grill-me/`, `create-issue/`, `implement-issue/`, `update-issue/` | The optional GitHub-issue workflow | Only when the manager decides one is warranted, and only after asking you |
| `.opencode/commit-style.md` | This repository's own commit convention, learned on first use | Before every commit |

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

## States, deduced and never stored

A request exists only for the length of the conversation that handles it: nothing is tracked as
draft, open, or in review anywhere outside that conversation. What persists across sessions is
the code itself, its commit history, and `.opencode/commit-style.md`.
