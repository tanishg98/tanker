# Architecture overview

Tanker is a thin opinionated layer on top of Claude Code. It introduces three primitives:

| Primitive | What it is | Where it lives |
|---|---|---|
| **Skill** | A slash command that does work in the current Claude Code conversation | `.claude/skills/<name>/SKILL.md` |
| **Agent** | A specialist spawned in an isolated context, returns a structured report | `.claude/agents/<name>.md` |
| **Rule** | An always-on operating principle loaded every session | `.claude/rules/*.md` |

## The three layers

```
┌─────────────────────────────────────────────────────────┐
│  Always-on rules                                        │
│  builder-ethos · code-standards · static-site-standards │
└─────────────────────────────────────────────────────────┘
                          │
         ┌────────────────┼─────────────────┐
         ▼                                  ▼
┌────────────────┐                ┌────────────────────┐
│  Skills (34)   │                │  Agents (9)        │
│  /cto          │  dispatches →  │  github-scout      │
│  /prd          │                │  pre-merge         │
│  /architect    │                │  prd-reviewer      │
│  /createplan   │                │  mvp-reviewer      │
│  /execute      │                │  site-eval         │
│  /analyst      │                │  explore           │
│  /ship         │                │  *-provisioner ×4  │
│  …             │                │                    │
└────────────────┘                └────────────────────┘
         │                                  │
         └────────────┬─────────────────────┘
                      ▼
         ┌────────────────────────┐
         │  outputs/<slug>/       │
         │  ├── state.json        │  ← high-level status
         │  ├── messages.jsonl    │  ← typed audit trail
         │  ├── prd/              │  ← phase artifacts
         │  ├── architecture.md   │
         │  ├── plan.md           │
         │  └── reviews/          │
         └────────────────────────┘
```

## How `/cto` orchestrates

`/cto` is the top-level autopilot. It dispatches skills and agents, gates merges, provisions infra, and writes everything to `outputs/<slug>/`.

```
intake → context (parallel: brain, refs) → reference (github-scout)
  → grill → benchmark? → prd → prd-reviewer → 🛑 GATE 1
  → architect → createplan → advisor
  → PROVISION (parallel: gh, supabase, vercel, railway)
  → BUILD (parallel: frontend, backend, data, content engineers)
  → pre-merge + autoresearch (per PR, bounded retry loop)
  → mvp-reviewer → 🛑 GATE 2
  → deploy → monitor → final report
```

Two human gates. Both pre-qualified by review agents. State checkpointed every phase.

## Provenance: messages.jsonl

Every artifact produced is wrapped in a typed Message envelope. See [messages](./messages.md). This is what makes runs replayable and cost-trackable.

## Quality rails

Always-on rules enforce craft. The `builder-ethos` rule encodes six principles — Boil the Lake, Search Before Building, Fix-First Review, No AI Slop, Safety Before Speed, Skill Chaining. The `code-standards` rule enforces type discipline and comment-the-why. The `static-site-standards` rule encodes the single-file-first, no-AI-slop UI bar.

Rails are architectural, not behavioral:

- Branch protection on main → no direct pushes
- Versioned migrations → every schema change is reversible
- Preview deploys mandatory → every change is reviewable before prod
- Healthcheck-gated rollback → prod auto-reverts on failure
- State checkpointed every phase → resumable from any failure point
- `/pre-merge` agent before any merge → autoresearch + review run before main is touched

## Cost ceiling

`--max-cost-usd <N>` (default 10). Tanker tracks spend in `messages.jsonl` (`cost_usd` per Message), warns at 70%, halts at 100%. Resume with a higher cap if needed.

## Read more

- [Message schema](./messages.md)
- [State.json schema](./state.md)
- [Human gates](./gates.md)
- [Provisioner agents](./provisioners.md)
