---
name: propose-upstream
description: Turns an idea about this layer itself — not the project it's installed in — into a GitHub issue filed against the repo named in .opencode/layer.json, so a fix found in one project can reach every project using this layer. The manager uses this only when it judges the idea actually belongs upstream, and only after asking the person; see the manager's "Optional workflows" section.
---

# Propose an improvement upstream

Requires `git` and `gh` (GitHub CLI), signed in: `gh auth status` must pass. Requires
`.opencode/layer.json` — if it's missing, this project's copy predates it; say so and offer to
run `/update-layer` first, which creates it, rather than guessing which repo to file against.

## Step 1 — Confirm this actually belongs upstream

Not every annoyance does. It belongs here, not in a local `create-issue`, when the fix would
help every project using this layer, not just this one:

- a bug in an agent, skill, or command file itself (a wrong instruction, a broken
  cross-reference, a rule that contradicts another one);
- a convention baked into the layer that doesn't fit how real projects actually work, found the
  hard way, in this project, during this session;
- a capability nothing in this layer covers, that this project ended up working around locally.

If the idea is really about this project's own code, stop and suggest `create-issue` instead.

## Step 2 — Light discovery

Three quick questions:

1. What happened in this project that surfaced it — the concrete moment, not a hypothetical.
2. What would "fixed" look like from the point of view of any project installing this layer,
   not just this one?
3. Did this project already work around it locally? If so, that workaround is useful evidence
   for the issue, even though it isn't necessarily the right general fix.

## Step 2b — Interrogate, if it's worth it

Same as `create-issue`: if the idea is thin, or would change how every project using this layer
behaves, run `grill-me` on it first. Skip it for anything light discovery already settled.

## Step 3 — Write the issue

A plain Markdown body, no external spec format:

```markdown
## What happened
<the concrete moment in this project that surfaced it>

## Proposal
<what should change in the layer itself, concrete enough to build from>

## Why this belongs upstream, not just here
<who else this would help, beyond this one project>

## This project's own workaround, if any
<what was done here meanwhile, as evidence - not necessarily the right general fix>
```

## Step 4 — The person's approval

Show the body, and name the repo it's about to be filed against (`.opencode/layer.json`'s
`repo`). Changes go back to Step 3. Nothing is created until they approve it explicitly.

## Step 5 — Create it

```bash
gh issue create --repo <layer.json's repo> --title "<imperative, one line>" --body-file <file>
```

## Principles

1. No implementation here — fixing it is a change to that other repository, for a session
   working in it, not this one.
2. The person approves the issue before it's created, and sees which repo it's going to.
3. Only for ideas about the layer itself; a project-specific idea goes to `create-issue`
   instead.
