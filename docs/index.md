# Tanker

> A Claude Code framework that ships deployed products from a one-line brief.

```bash
/cto "AI business analyst for Indian D2C sellers — connects 6 SaaS tools, chat with your data"
```

…and ~30 minutes of attention later, you have:

- A live production URL.
- A repo with branch protection, CI, versioned migrations.
- Provisioned Vercel + Railway + Supabase + GitHub.
- Sentry + analytics + uptime wired.
- A full audit trail of every artifact, agent, and decision in `outputs/<slug>/messages.jsonl`.

Tanker is **not** a code-generation library. It is a Claude Code skill + agent framework with two human gates, real infrastructure provisioning, and opinionated quality rails.

## Why use Tanker

| | Without Tanker | With Tanker |
|---|---|---|
| Brief → PRD | 1–2 days | ~5 minutes |
| PRD → architecture + plan | 1 day | ~10 minutes |
| Plan → deployed MVP | 1–4 weeks | ~3 hours |
| Bug fix end-to-end | 2–4 hours | ~25 minutes |
| Production deployment + monitoring | half a day | wired automatically |

The compression isn't because Tanker is faster at thinking. It's faster at *not skipping steps*. Every `/cto` run does the things you would have skipped — exhaustive PRD, real bug analysis pre-merge, MVP review at 9 dimensions, healthcheck-gated rollback. The cost of completeness with AI is near zero, but only if you wire the rails.

## What's different about Tanker

- **Two human gates pre-qualified by review agents.** Most autopilots either go fully autonomous (and ship slop) or stop everywhere (and waste your time). Tanker stops twice — at PRD, at MVP — but only after a review agent has pre-qualified the work. You see only what's worth seeing.
- **Real infrastructure provisioning.** GitHub repo, Supabase project, Vercel project, Railway service — all created via the official APIs from a vault that lives at `~/.claude/vault/credentials.json` (0600).
- **Resumable across sessions.** `state.json` checkpointed every phase. `/cto --resume <slug>` picks up exactly where you left off. `messages.jsonl` is the audit trail.
- **Local semantic retrieval.** Tanker indexes your Obsidian vault + curated GitHub references into local ChromaDB. `/cto` Phase 1 retrieves from your accumulated knowledge — not generic GitHub search.
- **Opinionated quality rails.** Builder-ethos rules are always on: Boil the Lake, Search Before Building, No AI Slop (with a published ban list), Safety Before Speed, Skill Chaining.
- **Cost ceiling.** `--max-cost-usd` argument, default $10. Tanker tracks spend in `messages.jsonl`, warns at 70%, halts at 100%.

## Get started

1. **Install:** `bash <(curl -fsSL https://raw.githubusercontent.com/tanishg98/tanker/main/install.sh)`
2. **Add credentials:** `/vault-add github vercel supabase anthropic`
3. **First run:** `/cto "build me a todo app with auth"`

→ [Detailed install guide](./getting-started/install.md)

## How it compares

- [Tanker vs MetaGPT](./comparisons/metagpt.md) — most-asked comparison.
- [Tanker vs AutoGen](./comparisons/autogen.md)
- [Tanker vs CrewAI](./comparisons/crewai.md)
- [Tanker vs Aider](./comparisons/aider.md)
- [Tanker vs gstack](./comparisons/gstack.md)

## License

MIT. Built by [Tanish Girotra](https://github.com/tanishg98).
