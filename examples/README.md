# Tanker Examples

Five worked examples — one per use-case Tanker is built for. Each example has:

- `brief.md` — the one-line product brief that kicked off the run.
- `transcript.md` — the captured `/cto` (or single-skill) run, phase by phase.
- `outputs/` — the actual artifacts the run produced (PRD, plan, code, screenshots, deploy URLs).

These are the canonical "show me what Tanker does" references. Read these before you read SKILL.md files.

## The five

| Example | What it shows | Live? | Recommended for |
|---|---|---|---|
| [saas-mvp/](./saas-mvp/) — **Persona Studio** | `/cto` end-to-end. Brief → deployed product with auth + DB + UI | [✅ live](https://persona-studio-lime.vercel.app) | First-time users |
| [static-site/](./static-site/) | `/static-site-replicator` + `/design-shotgun` flow | scaffold | Marketing pages, landing sites, portfolios |
| [browser-extension/](./browser-extension/) | `/browser-extension-builder` for a Chrome MV3 extension | scaffold | Productivity tools, page-modifiers |
| [bug-fix/](./bug-fix/) | `/explore` → `/debug` → `/test-gen` → `/ship` flow on an existing repo | scaffold | Daily engineering work |
| [data-analysis/](./data-analysis/) | `/analyst` ReAct loop on a real dataset | scaffold | Investigation, KPI work, attribution |

**Persona Studio** is a real shipped product built with `/cto`: India-first AI influencer studio, currently live in private beta. The other four are scaffolds — fill them in by running the brief and pasting the captured run.

## How to read a transcript

Each `transcript.md` is structured as:

```
# <Example name>

## The brief
> One-line ask.

## What Tanker did
1. Phase 1: …
2. Phase 2: …
…

## What was produced
- File X (link)
- File Y (link)

## What the human did
- Reviewed PRD at gate 1, fed back …
- Approved MVP at gate 2

## Final output
- Repo: …
- Production URL: …
- Time elapsed: …
- Cost: $… (from --audit)

## Honest debrief
- What went well.
- What broke.
- What I'd change.
```

Honest debriefs are the most valuable part. Real runs always have rough edges; the transcripts here don't pretend otherwise.

## Contributing your own example

PRs welcome. Bar:
- Real run, not synthetic.
- Include the `messages.jsonl` from the run (under `outputs/<slug>/`).
- Honest debrief — include what broke, not just what shipped.
- Redact secrets and any private context.
