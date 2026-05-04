# Tanker vs MetaGPT

[MetaGPT](https://github.com/FoundationAgents/MetaGPT) is a multi-agent code-generation framework — Python-first, role-playing agents, ICLR 2024 paper. Tanker solves a different problem: shipping deployed products from a brief, on Claude Code, with human gates.

## TL;DR

- **Tanker ships deployed products. MetaGPT writes code on disk.** Different scope.
- **Tanker has two human gates pre-qualified by review agents. MetaGPT runs fully autonomous.** Different operator model.
- **Tanker is Claude Code-native and opinionated. MetaGPT is provider-generic and taste-neutral.** Different surface.

If you want a generic Python framework you can drop into any LLM stack, MetaGPT is the right tool. If you want an opinionated Claude Code-native pipeline that ends in a deployed URL with monitoring wired, Tanker is the right tool.

---

## What you get with Tanker that you don't get with MetaGPT

### 1. **A deployed URL, not a code folder**

Tanker's `/cto` autopilot provisions real infrastructure via official APIs:

- GitHub repo with branch protection, CI, secrets pushed from a vault
- Supabase project with RLS migrations + Management API integration
- Vercel project linked to GitHub with preview deploys per PR
- Railway service with healthcheck-gated rollback

The end state is a live production URL with monitoring (Sentry + Plausible + uptime). MetaGPT stops at a code repo on disk.

### 2. **Two human gates with pre-qualification**

Tanker pauses at exactly two points: post-PRD and post-MVP. Each gate is pre-qualified by a review agent (`prd-reviewer`, `mvp-reviewer`) that runs an exhaustive check. The owner only sees the gate after the agent returns PASS. Total owner attention per `/cto` run: ~30 minutes.

MetaGPT trusts the agent pipeline end-to-end. No human checkpoints.

### 3. **Cost ceiling enforced by the framework**

`/cto --max-cost-usd <N>` (default $10). Tanker tracks spend per Message envelope, warns at 70%, halts gracefully at 100%. Resume with a higher cap if needed. Predictable spend matters for solo builders.

MetaGPT has no in-framework cost ceiling.

### 4. **Resumable across sessions**

`state.json` checkpointed every phase. `messages.jsonl` is the typed audit trail. `/cto --resume <slug>` picks up exactly where you left off. Laptop dies mid-build — no data lost.

MetaGPT runs are per-process, not designed for resume.

### 5. **Local semantic retrieval over your corpus**

`brain-index` indexes your Obsidian vault into local ChromaDB. `refs-index` indexes curated GitHub repos you find inspiring. `/cto` Phase 1 retrieves from both before any other step — the orchestrator pulls from your accumulated knowledge, not generic GitHub search.

MetaGPT starts every run cold.

### 6. **Opinionated quality rails always on**

Tanker's `builder-ethos` rule loads every session and encodes:

- Explicit **No AI Slop ban list** (no purple gradients, no centered everything, no "Welcome to X" hero copy, no skipped heading levels)
- **Boil the Lake** — full implementation every time, not 90%-good-enough
- **Search Before Building** — three-layer knowledge model (tried-and-true → new-and-popular → first principles)
- **Safety Before Speed** — irreversible actions require confirmation
- **Skill Chaining** — every skill ends with a handoff to the next

MetaGPT is taste-agnostic by design. Output quality depends on user prompts.

### 7. **34 specialized skills + 9 agents**

Tanker exposes a full pipeline as composable slash commands (`/grill` → `/benchmark` → `/prd` → `/architect` → `/createplan` → `/execute` → `/ship` → `/deploy` → `/monitor` → `/retro` → `/learn`). Plus dedicated agents for review (pre-merge, prd-reviewer, mvp-reviewer, site-eval), research (github-scout), and provisioning (gh / supabase / vercel / railway).

MetaGPT exposes ~5 roles (PM, Architect, Engineer, QA).

### 8. **JSON sidecar contracts for every artifact**

`/prd`, `/architect`, `/createplan`, `pre-merge` all produce machine-readable JSON sidecars validated against schemas in `.claude/schemas/`. Reviewer agents read JSON, not parse markdown. The retry loop in Phase 5 decides on `verdict + findings[].fix_kind`, not regex.

MetaGPT outputs are markdown; downstream tooling must re-parse.

### 9. **Cross-model peer review**

`/advisor` runs a Sonnet pass over Opus output (or vice versa) to catch undefended claims before stakeholder send. Different families catch different blind spots.

MetaGPT has no equivalent hook.

### 10. **Real shipped product as proof**

Persona Studio ([persona-studio-lime.vercel.app](https://persona-studio-lime.vercel.app)) is a real product built end-to-end with one `/cto` brief. Indian-market AI influencer studio, currently in private beta.

---

## Side-by-side

| | MetaGPT | Tanker |
|---|---|---|
| **One-line entry** | `metagpt "build a snake game"` | `/cto "<brief>"` |
| **Output** | Local code repo | Deployed product (preview URL + prod URL + repo + monitoring) |
| **Human gates** | None — fully autonomous | Two mandatory gates (PRD, MVP), pre-qualified by review agents |
| **Real infra provisioning** | No | Yes — gh + supabase + vercel + railway provisioner agents |
| **Quality gates** | One QA agent | pre-merge + autoresearch-review + prd-reviewer + mvp-reviewer + site-eval + security-review |
| **Cross-model peer review** | No | `/advisor` runs another model over your model's output |
| **Resumability** | Per-run, ephemeral | `state.json` checkpointed every phase; `--resume` works across sessions |
| **Cost ceiling** | None | `--max-cost-usd` (default $10), tracked per Message |
| **Audit trail** | Implicit in LLM logs | `messages.jsonl` with typed envelope per artifact |
| **Context retrieval** | None | brain-index (Obsidian vault) + refs-index (curated GitHub) |
| **Roles surface** | PM, Architect, Engineer, QA (~5) | 34 skills + 9 agents |
| **Distribution** | Pip install | Drop `.claude/` into any project |
| **License** | MIT | MIT |

---

## When MetaGPT is the better choice

Honest:

- You want a **generic Python framework** that works across LLM providers (OpenAI, Azure, local, Claude). Tanker is Claude Code-native.
- You want **fully autonomous runs** with no human checkpoints — you're running short tasks where human attention is the bottleneck.
- You're studying multi-agent SOPs as a **research framework**.
- You need **40+ runnable examples** for inspiration. Tanker has 5.
- You're **not on Claude Code.**

---

## When Tanker is the better choice

- You're already on **Claude Code** and want to stop re-explaining conventions every session.
- You want a **deployed URL**, not a code repo. Provisioning + deploy + monitoring should be in scope, not your problem to wire afterwards.
- You want **human gates without attention burn** — you want to be the operator, not the QA bot.
- You have an **Obsidian vault** or a **curated GitHub reference library** you want your autopilot to draw from.
- You want **opinionated quality rails** (No AI Slop ban list, semantic HTML, mobile-first, light-mode-for-SMB-tools).
- You want **predictable spend** — `--max-cost-usd` cap.
- You want runs to be **resumable across sessions** with full audit trail.

---

## The bottom line

These are different products solving different problems. MetaGPT is a research-grade multi-agent framework — generic, autonomous, multi-provider. Tanker is an opinionated production pipeline — Claude Code-native, human-gated, deploys to real infrastructure.

Both are MIT. Pick the one that matches your operator model.
