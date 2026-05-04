# Show HN — submission package

## Title (≤80 chars)

```
Show HN: Tanker — Claude Code framework that ships deployed products from a brief
```

Alt versions to A/B (only one will be used; pick on the day):

```
Show HN: A Claude Code framework with two human gates and real provisioning
Show HN: Tanker – /cto "<brief>" → live URL in ~3 hours, 30 min owner attention
Show HN: Tanker, an opinionated Claude Code skill framework I built solo
```

## URL

```
https://github.com/tanishg98/tanker
```

(Or `https://tanker.dev` once docs are live — Hacker News prefers the docs URL if it has a clean landing page with the demo GIF.)

## First comment (post immediately after submission)

```
I'm Tanish — CEO's Office at Shiprocket (India), building everything with AI. I built Tanker because I kept hitting the same problem: Claude Code is great at code but blank-slate at product workflows. Every session, I was re-explaining the same conventions, the same quality bar, the same handoffs.

Tanker is a `.claude/` folder you drop into any project — 34 slash skills, 9 specialist agents, 3 always-on rules. The headline command is `/cto "<one-line brief>"` which runs the whole pipeline: brief → /grill → /prd → architect → plan → provision (GitHub + Supabase + Vercel + Railway via real APIs) → parallel build subagents → mvp review → deploy. Two human gates pre-qualified by review agents — you spend ~30 min total reviewing.

A few choices that came from real failures:

- Two human gates instead of fully autonomous. I tried full-auto for a week. It shipped slop. The gates are at the points where human judgment compounds (PRD, MVP).
- Cost ceiling. Default $10 per /cto run. Tracked per-message in messages.jsonl. Halts gracefully, resumes with a higher cap.
- Typed Message envelope (cause_by, sent_from, send_to) — borrowed from MetaGPT. Makes runs replayable, auditable, cost-trackable.
- SOP triplet prompt pattern (Constraints + Reference + Output Format). Borrowed from MetaGPT's PRD action. Cuts skill output variance significantly.
- Local semantic retrieval — brain-index over an Obsidian vault + curated GitHub references. /cto Phase 1 retrieves from your own corpus before doing anything else.

Honest comparison page with MetaGPT, AutoGen, CrewAI, Aider, and gstack: https://tanker.dev/comparisons/metagpt/

Stuff I'd love feedback on:
- Is the two-gates pattern too restrictive? Too few?
- The /analyst skill (Plan → Execute → Reflect → Decide on real Python) — would you trust it to run code on your data?
- The cost ceiling default of $10 — too high, too low?

Source: https://github.com/tanishg98/tanker (MIT)
```

## Don't

- Don't title with "I built X" — HN softly downvotes self-promotion phrasing in titles.
- Don't include emojis in the title.
- Don't ask for upvotes anywhere. Ban-hammer.
- Don't post a second time if the first dies. One shot per project per quarter.

## Reply playbook

Pin this on your monitor while the post is live:

| If they say | Reply |
|---|---|
| "How is this different from MetaGPT?" | Link comparison page + 1-paragraph summary. |
| "Why Claude Code only?" | "Today, yes. Multi-LLM is on the roadmap (steal #10 from MetaGPT)." |
| "This is just prompt engineering" | "Most of it is. The non-trivial parts are: typed Message schema, JSON sidecar contracts, the orchestrator's retry loop, and the provisioner agents." |
| "Does it actually work?" | Link the SaaS MVP example transcript. |
| "Show me a video" | Link the demo GIF. If you don't have one yet — **don't launch.** |
| "Is this open source?" | "MIT. PRs welcome." |
| "Can I use it commercially?" | "Yes — MIT." |
| Any vendor-bias question (lock-in to Anthropic) | "Fair point. Multi-LLM is on the roadmap. Today Tanker is opinionated about Claude Code." |
| Any rude or dismissive comment | Don't reply. Reply only to substantive critique. |

## Front page math

To stay on the front page after launch hour:

- 50+ upvotes in first 90 minutes → you're on /front.
- 10+ thoughtful comments in first 2 hours → algorithm rewards engagement.
- One comment from you within 5 minutes of submission → seeds discussion.

Stay at your computer for the first 4 hours after submission. Reply within 10 minutes of every substantive comment.
