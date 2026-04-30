# r/ClaudeAI post

## Title

```
I built a Claude Code framework with 34 slash skills, 9 agents, and 2 human review gates — runs end-to-end from a one-line brief
```

## Body

```
Hey r/ClaudeAI,

Sharing Tanker — what I've been building on top of Claude Code for the last few months.

Headline: `/cto "<one-line brief>"` → live deployed product (~3 hours, ~30 min of my attention).

Why I built it:
Claude Code is genuinely powerful, but every session starts cold. Conventions, handoffs, quality bar — I was re-explaining all of it. Tanker is a `.claude/` folder you drop in. Skills auto-load. Always-on rules apply every session. State persists across runs.

The /cto pipeline:
- intake → context (parallel: brain-index + refs-index)
- /grill → /benchmark → /prd → prd-reviewer → 🛑 GATE 1 (human PRD review)
- /architect → /createplan → /advisor (cross-model peer review)
- PROVISION (parallel: gh + supabase + vercel + railway via real APIs)
- BUILD (parallel: frontend + backend + data + content engineers as subagents)
- /pre-merge + /autoresearch-review per PR (bounded retry loop, max 2)
- mvp-reviewer → 🛑 GATE 2 (human MVP review)
- /deploy → /monitor → final report

State checkpointed every phase. Resumable across sessions via /cto --resume <slug>.

A few things I'm proud of:
- Two human gates pre-qualified by review agents — best of both autopilot worlds.
- Cost ceiling: --max-cost-usd, default $10, halts gracefully.
- Typed Message envelope (cause_by, sent_from, send_to) — borrowed from MetaGPT, makes runs replayable + auditable.
- JSON sidecar schemas — every skill output is machine-readable. Reviewer agents read JSON, not parse markdown.
- Local semantic retrieval — brain-index over Obsidian vault, refs-index over curated GitHub repos.
- Always-on rules: builder-ethos (No AI Slop ban list), code-standards, static-site-standards.

Repo: https://github.com/tanishg98/tanker (MIT)
Docs: https://tanker.dev
Comparison vs MetaGPT, AutoGen, CrewAI, Aider, gstack: https://tanker.dev/comparisons/

Open to feedback — what would you want differently?
```

## Don't

- Don't crosspost word-for-word from r/LocalLLaMA. Different community vibes.
- Don't ask for upvotes. Mods are strict.
