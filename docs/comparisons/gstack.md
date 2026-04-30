# Tanker vs gstack

[gstack](https://github.com/garrytan/gstack) is Garry Tan's Claude Code skill+rule kit. Tanker is the parallel project — same primitives (Claude Code skills and rules), different opinions.

## TL;DR

- Same category. Different opinions.
- gstack is the original. Tanker borrows the pattern, ships its own opinionated layer.

## What Tanker has that gstack doesn't

- **`/cto` autopilot orchestrator** — gstack chains skills manually; Tanker has one command that runs the full pipeline.
- **`/ui-hunt`** — automated category-specific reference research before any UI work.
- **`/design-shotgun`** — 4 working HTML prototypes (gstack does image mockups).
- **Project brain** — per-project `.claude/brain.md` via `/learn`, persisted across sessions.
- **brain-index + refs-index** — local semantic retrieval over Obsidian + curated GitHub.
- **Session continuity** — `/context-save` + `/context-restore` checkpoint to `.claude/context.md`.
- **Provisioner agents** — real GitHub + Supabase + Vercel + Railway provisioning from a vault.
- **Two human gates** — pre-qualified by review agents.
- **Typed Message schema** — `messages.jsonl` with provenance.
- **JSON sidecar schemas** — every skill output is machine-readable (validated against `.claude/schemas/`).
- **Cost cap** — `--max-cost-usd` ceiling.

## What gstack has that Tanker doesn't

- **Compiled Chromium binary for browser automation** — Tanker is pure Claude Code, no compiled deps.
- **`/careful`, `/freeze`, `/guard` safety primitives** — Tanker folds safety into `builder-ethos` Principle 5 (always on).

## Skill chaining

gstack hands off manually. Tanker enforces chaining via `builder-ethos` Principle 6 — every skill ends with a handoff line pointing to the next skill in the chain.

## When to use which

**gstack if** you want the original Garry Tan stack and you don't need autopilot.

**Tanker if** you want autopilot, provisioning, deploy, and the Indian-D2C / Anthropic-editorial taste opinions baked in.

## Credit

Tanker's primitives (slash skills, always-on rules, agents) follow gstack's pattern. Tanker is what happens when you take that pattern and bake in opinions for a specific operator (Indian product head shipping AI tools).
