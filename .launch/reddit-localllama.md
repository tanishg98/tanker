# r/LocalLLaMA post

## Title

```
Tanker: a Claude Code framework that turns a one-line brief into a deployed product. Open-sourced what I've been using internally.
```

## Body

```
Hey r/LocalLLaMA,

I've been using Claude Code as my daily driver for ~6 months and kept hitting the same wall: every session starts blank. Same conventions to re-explain, same handoffs to wire, same quality bar to enforce.

I built Tanker to fix that. It's a `.claude/` folder you drop into any project — 34 slash skills, 9 agents, 3 always-on rules. Headline command is `/cto "<one-line brief>"` which runs the whole pipeline:

  brief → /grill → /prd → architect → plan → provision (gh + supabase + vercel + railway) → parallel build subagents → mvp review → deploy → monitor

Two human gates (PRD + MVP), both pre-qualified by review agents. You only see what's worth seeing. Total owner attention per run: ~30 minutes for a deployed product.

A few things I borrowed from MetaGPT:
- Typed Message envelope schema (cause_by, sent_from, send_to)
- SOP triplet prompt pattern (Constraints + Reference + Output Format)
- Bounded review-retry loop (max 2)
- DataInterpreter pattern → my /analyst skill

A few things that are Tanker-specific:
- Real provisioning (not just code generation)
- Cost ceiling (--max-cost-usd, default $10, halts gracefully)
- Resumability via state.json + messages.jsonl (typed audit trail)
- Local semantic retrieval over your Obsidian vault + curated GitHub repos
- Opinionated quality rails (No AI Slop ban list, Boil-the-Lake principle)

Today it's Claude Code-only. Multi-LLM is on the roadmap (took the cue from MetaGPT's config2.yaml pattern).

Repo: https://github.com/tanishg98/tanker (MIT)
Docs + comparisons: https://tanker.dev
Five worked examples: https://github.com/tanishg98/tanker/tree/main/examples

Honest with this community: I'm not a full-time AI infra builder. I work out of Shiprocket's CEO Office building everything with AI, and I need things that ship fast. Tanker is what I needed; if it's useful to you, great. PRs welcome.

Most useful feedback: is the two-gates pattern too restrictive? Too few? What would you change?
```

## Don't

- Don't post on Saturday/Sunday. Tuesday-Thursday performs.
- Don't reply to "this is just X" with defensive prose. Either link the comparison page or skip.
- Don't link a YouTube video without the GIF — Reddit prefers visual.
