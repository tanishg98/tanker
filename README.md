# tanker

> A structured set of Claude Code skills, agents, and rules that replaces ad-hoc AI prompting with a repeatable, high-craft engineering workflow.

Built by [Tanish Girotra](https://github.com/tanishg98) · MIT License

---

## The Problem

Claude Code is powerful out of the box — but without structure, every session starts from scratch. You get inconsistent output, half-finished implementations, no quality gates, and the same corrections over and over.

tanker fixes that. It gives Claude a **defined role for every phase of a build** — from product thinking to deployment — with explicit handoffs, quality checks, and a project brain that remembers what was learned.

---

## Autopilot Mode — `/cto`

One command: brief → live product. tanker turns into your CTO with a pool of subagent engineers AND human-in-the-loop gates so you stay in control of strategy and final QA.

```
/cto "AI business analyst for Indian D2C sellers — connects 6 SaaS tools, chat with your data"
```

What it does end-to-end:

```
intake → state.json created
  └── CONTEXT LOAD (parallel)
      ├── .claude/brain.md (project memory)
      ├── ~/.claude/projects/.../memory/ (auto-memory)
      ├── brain-index — semantic retrieval over Obsidian vault
      └── refs-index   — semantic retrieval over curated GitHub repos
  └── github-scout: Tier 0 = curated refs, Tier 1 = wider GH search
      └── /grill → /benchmark? → /prd  (exhaustive — every feature → screen,
                                          every screen → all states, HTML mocks)
          └── prd-reviewer agent → BLOCK / PASS WITH FIXES / PASS
              └── 🛑 GATE 1 — Human review of the PRD bundle
                  └── owner replies "approved" / "fix: …" / "abort"
              └── /architect → /createplan → /advisor
                  └── PROVISION (parallel)
                      ├── gh-provisioner       repo + branch protection + secrets
                      ├── supabase-provisioner project + RLS + Management API
                      ├── vercel-provisioner   project linked to GH + env vars
                      └── railway-provisioner  service + healthcheck (if backend)
                  └── BUILD (parallel engineering pool)
                      ├── frontend-engineer → /design-shotgun → code → PR
                      ├── backend-engineer  → /backend-builder → PR
                      ├── data-engineer     → versioned migrations → PR
                      └── content-engineer  → copy + SEO → PR
                  └── /pre-merge + /autoresearch-review per PR
                  └── spin up LOCAL preview → mvp-reviewer agent
                      └── 🛑 GATE 2 — Human review of the working MVP
                          └── owner replies "approved" / "fix: …" / "abort"
                  └── /deploy production → smoke test → live (auto-rollback on health fail)
                  └── /monitor (Sentry + Plausible + uptime)
                  └── final report: prod URL, repo URL, dashboards
```

**Two human gates pre-qualified by review agents.** You only see work that has passed an automated check. Total owner attention: ~30 minutes (two reviews) for a deployed product. State checkpointed to `outputs/<slug>/state.json` so any session can `/cto --resume <slug>`.

Why autopilot is production-grade: rails are architectural, not behavioral. Branch protection, versioned migrations, mandatory preview deploys, healthcheck-gated rollback, state checkpointing — your local sandbox enforces all of these too.

**Pre-flight (one-time, ~10 minutes):**

```bash
# Credentials for the provisioner agents
/vault-add github vercel supabase anthropic
# (railway / sentry / plausible if needed)

# Local semantic retrieval over your Obsidian vault
bash .claude/skills/brain-index/setup.sh                    # ~3 min, ~200MB
~/.claude/brain-index/venv/bin/python \
  .claude/skills/brain-index/index.py                       # ~5 min for ~1000 notes

# Curated GitHub references that shape /cto's output toward your taste
/cto-add-ref add https://github.com/<owner>/<repo> --why "..." --tags ...
```

Credentials live in `~/.claude/vault/credentials.json` (0600, never committed). Embeddings live in `~/.claude/brain-index/data/` (local-only, never leave the machine).

---

## The Workflow

### Product Build (new product or major feature)

```
/grill → /ui-hunt → /architect → /createplan → /execute → /autoresearch-review → /ship → /deploy → /monitor
```

Or, for the autopilot version of the above: `/cto "<brief>"`

### Feature on Existing Product

```
explore agent → /createplan → /execute → /autoresearch-review → /ship
```

### UI/UX First

```
/ui-hunt → /design-shotgun → /execute (or /static-site-replicator) → site-eval agent
```

### Session Management

```
/context-restore → [work] → /context-save
```

### Weekly Improvement

```
/retro → /learn
```

---

## Core Workflow Table

| Phase | Skill/Agent | What happens |
|-------|-------------|-------------|
| Think | `/grill` | 6 YC-style forcing questions before writing code. Surfaces bad assumptions, defines the 10-star product, produces a Product Brief. (formerly `/office-hours`) |
| Research | `/ui-hunt` | Finds best-in-class products in your category, extracts design intelligence, produces a Reference Brief. Ends AI slop at the root cause. |
| Design | `/design-shotgun` | Generates 4 real HTML/CSS design directions. You pick one. Breaks the "first generic output wins" pattern. |
| Explore | `explore` agent | Maps the codebase, traces data flows, surfaces risks before any code is written. |
| Architect | `/architect` | Component diagram, data model, API contracts, decision log, risk register for complex systems. |
| Plan | `/createplan` | Scoped, step-sized plan with dependency analysis, risk-first ordering, and a confidence check. |
| Build | `/execute` | Implements one step at a time, updates the tracker, writes a status report after each. |
| Gate | `pre-merge` agent | Combined quality + bug gate — returns BLOCK / PASS WITH FIXES / PASS before any merge. |
| Ship | `/ship` | Sync main, run tests, commit, push, open structured PR. |
| Deploy | `/deploy` | Env vars, CI/CD, health checks, rollback on Vercel/Railway/Fly/Docker. |
| Observe | `/monitor` | Sentry, uptime, structured logging, analytics. |
| Improve | `/reflect` | Traces failures to the specific config that caused them, applies surgical fixes. |
| Remember | `/learn` | Writes conventions, decisions, pitfalls, and preferences to `.claude/brain.md`. Persists across sessions. |
| Review | `/retro` | Weekly retrospective. Reads git history + brain. Writes learnings back. |

---

## Skills (34 total)

### Autopilot

**`/cto`** — NEW
Top-level orchestrator. Takes a one-line product brief, runs the entire build → deploy → monitor lifecycle by dispatching skills and provisioner subagents in parallel. State checkpointed to `outputs/<slug>/state.json` so any session can resume with `/cto --resume <slug>`. Default mode is autopilot; pass `--gated` for human approval at each phase.

**`/vault-add`** — NEW
Registers a credential in `~/.claude/vault/credentials.json` (0600 perms). Provisioner subagents read from the vault — never log values, never include them in commits or chat. Supports github, vercel, railway, supabase, cloudflare, anthropic, openai, stripe, resend, sentry, plausible.


### Product & Strategy

**`/grill`** — NEW
YC-style forcing questions before writing any code. Six questions that reframe the product, surface the killer assumption, and define the 10-star version. Produces a Product Brief that feeds into `/architect` or `/createplan`.

**`/ui-hunt`** — NEW
The root cause of AI slop is building without a reference. This skill finds the top 3 best-in-class products in your category, extracts their design intelligence (palette, typography, layout, copy tone), and produces a Reference Brief. Unique to tanker — doesn't exist in any other kit.

### Design

**`/design-shotgun`** — NEW
Generates 4 distinct HTML/CSS design directions — each a working mini-prototype with a real palette, fonts, hero section, and features block. Outputs a comparison page at `outputs/design-shotgun/`. You pick a direction; it becomes the approved Design Brief for the full build.

**`/static-site-replicator`**
Replicate any reference website as a polished static HTML/CSS/JS site with new brand assets.

### Planning & Execution

**`/explore`** — via `explore` agent
Reads the codebase autonomously before any feature work. Returns a structured report covering affected files, integration points, constraints, and open questions.

**`/architect`**
System design before complex builds. Produces: component diagram, data model, API contracts, decision log, risk register.

**`/createplan`**
Creates a structured implementation plan with dependency analysis, risk-first ordering, and a confidence check on every step.

**`/execute`**
Implements the plan one step at a time. After each step: marks it complete, writes a status report, and stops — so you stay in control.

### Building

**`/backend-builder`**
Full backend lifecycle: Express/Fastify/Hono/FastAPI/Supabase, project scaffold, routes, validation, auth, error handling, DB, security checklist.

**`/browser-extension-builder`**
Chrome and Firefox extensions (Manifest V3): architecture decision, message passing, `chrome.storage`, CSP-safe patterns, security checklist.

**`/mobile-app-builder`**
PWA or Expo/React Native — decides which path based on what native APIs you need.

**`/deploy`**
Production deployment: env vars, GitHub Actions CI/CD, platform-specific setup, health check endpoint, rollback procedure.

**`/monitor`**
Post-ship observability: Sentry, PostHog/Plausible, Better Uptime, Pino + Axiom.

### Release

**`/ship`** — NEW
Complete release workflow: sync main, run tests, commit, push, open a structured PR. Replaces ad-hoc `git push and hope`. Hard gate: will not push failing tests.

### Code Quality

**`/autoresearch-review`** *(also `/ar-review`)*
Pre-merge deep bug analysis. Tags every changed function by type, runs failure mode catalogue, enumerates edge cases, scores P0–P3. Returns: BLOCK / MERGE WITH FIXES / MERGE SAFE.

**`/debug`**
Systematic debugging from symptom to root cause using a structured elimination method. Identifies the exact line and condition before any fix is written.

**`/test-gen`**
Generates targeted tests ordered by bug probability. Phase 0: framework detection.

**`/security-review`**
OWASP Top 10 + threat modeling. Run before any public launch.

**`/peer-review`**
Triages human reviewer feedback: Accept / Accept (wrong fix) / Context Missing / Reject. Produces a prioritised action plan.

**`/simplify`**
Reviews changed code for reuse, quality, and efficiency. Fixes what it finds.

### Self-Improvement

**`/reflect`**
Self-correction skill. Reads `.claude/reflect-log.md` first to detect repeat failures, then traces the failure to its config, applies a surgical fix.

**`/autoresearch-review`**
Also runs as a pre-merge gate — see Code Quality above.

### Project Memory

**`/learn`** — NEW (Project Brain)
Writes and reads `.claude/brain.md` in each project — storing conventions, decisions, pitfalls, and preferences. Run at end of any session. The brain is read automatically by `explore` and `/retro`.

**`/retro`** — NEW
Weekly engineering retrospective. Reads git history + brain. Identifies what shipped, what broke, what slowed things down. Writes learnings back to the brain.

**`/context-save`** — NEW
Session checkpoint. Commits in-progress work with WIP prefix, writes `.claude/context.md` with current state, decisions made, and ordered next steps.

**`/context-restore`** — NEW
Session recovery. Reads `.claude/context.md` and recent git history to reconstruct where you left off. Gets you back to productive work in under 60 seconds.

### Project Utilities

**`/create-issue`** — Captures a bug or feature as a structured issue document mid-flow.

**`/documentation`** — Updates `CHANGELOG.md` and inline docs after a feature or fix.

**`/learning`** — Explains a concept in three progressive levels with a peer-to-peer tone.

**`/peer-review`** — Triages human reviewer feedback into Accept / Reject / Context Missing.

**`/architect`** — System design for complex multi-component projects.

---

## Agents (9 total)

Agents run autonomously on a focused task in their own isolated context. Read-only agents return structured reports; provisioner agents have scoped write access to one external service (their job is to produce infra and report back).

### Read-only review agents

| Agent | When to run | What it does |
|-------|-------------|-------------|
| `explore` | Before planning any feature or bug fix | Maps codebase, traces data flows, surfaces integration points and risks, returns numbered open questions |
| `pre-merge` | Before every PR merge — no exceptions | Combined quality review + Karpathy-style bug analysis. Returns BLOCK / PASS WITH FIXES / PASS |
| `review` | On any significant code change | Severity-classified code review (CRITICAL/HIGH/MEDIUM/LOW). Every finding gets a concrete fix. |
| `site-eval` | After any static site build, before delivery | 9-dimension audit: completeness, typography, brand, animations, responsiveness, images, technical hygiene, performance, AI slop detection |

### Research agent

| Agent | When to run | What it does |
|-------|-------------|-------------|
| `github-scout` | Before `/architect` on any new build | Searches GitHub for ≥5 prior-art repos, reads READMEs + manifests, returns a Reference Brief — convergent stack, patterns to lift, footguns observed, first-principles override |

### Provisioner agents (autopilot infra)

Read from `~/.claude/vault/credentials.json`, talk to one external service, return JSON metadata. All idempotent — re-running on existing infra is safe.

| Agent | Service | What it does |
|-------|---------|-------------|
| `gh-provisioner` | GitHub | Creates repo, sets branch protection on main, pushes secrets from vault, scaffolds `.gitignore` and CI workflow |
| `supabase-provisioner` | Supabase | Creates project via Management API, scaffolds versioned migrations + RLS, captures keys to vault, pushes secrets to GitHub |
| `vercel-provisioner` | Vercel | Creates project linked to GitHub, pushes env vars from vault, configures custom domain, triggers preview deploy on every PR |
| `railway-provisioner` | Railway | Creates project + service, attaches Postgres if needed, configures healthcheck on `/health`, restart policy ON_FAILURE/3 |

**Skills vs Agents — the key difference:**

| | Skills | Agents |
|---|---|---|
| Invoked with | `/skill-name` slash command | `Agent` tool (spawned by Claude) |
| Runs in | Current conversation context | Separate isolated context |
| Can modify files | Yes — skills do the work | No — read-only analysis only |
| Has access to conversation history | Yes | No — starts fresh |
| Used for | Active building, planning, generating | Research, review, pre-launch checks |
| Example | `/execute` builds code | `explore` agent reads code and reports back |

Think of it this way: **skills are Claude doing work**. **Agents are Claude dispatching a specialist to investigate and report back**.

---

## Skill Chaining

Skills have a natural order. Each skill ends with a clear handoff to the next — either automatic or prompted.

**The product build chain:**
```
/grill → /ui-hunt → /design-shotgun → /architect → /createplan → /execute → /autoresearch-review → /ship → /deploy → /monitor → /learn
```

**How chaining works:**
- Some transitions are **automatic**: `/ui-hunt` immediately flows into `/design-shotgun` when you confirm. `/execute` moves to the next step without asking.
- Some transitions are **prompted**: after `/grill`, Claude asks "Ready to run `/architect`?" — you confirm before it proceeds.
- Chaining rules are in `builder-ethos.md` Principle 6 — always loaded.

**To chain manually:** just say "continue" or invoke the next skill. Claude knows the sequence.

---

## Rules (Always On)

Rules load automatically in every session. No invocation needed.

**`builder-ethos`** — Six core principles:
1. **Boil the Lake** — AI makes completeness cheap. Full implementation every time.
2. **Search Before Building** — Tried-and-true → new-and-popular → first principles.
3. **Fix-First Review** — Every finding is AUTO-FIX or ASK before action.
4. **No AI Slop** — Explicit ban list of low-craft AI patterns.
5. **Safety Before Speed** — Irreversible actions require confirmation. List of what always needs a confirm.
6. **Skill Chaining** — Skills prompt or auto-invoke the next skill. You always know what comes next.

**`code-standards`** — Type safety, comment discipline, pattern consistency.

**`static-site-standards`** — Single-file first, no frameworks, mobile-first, IntersectionObserver animations, semantic HTML, Unsplash images, eval gate.

---

## Installation

Copy the `.claude/` folder into any project:

```bash
git clone https://github.com/tanishg98/tanker
cp -r tanker/.claude your-project/.claude
```

Skills are immediately available as `/skill-name` commands in Claude Code.

---

## Repo Structure

```
.claude/
├── agents/
│   ├── explore.md                    — codebase exploration (read-only)
│   ├── pre-merge.md                  — mandatory quality + bug gate
│   ├── review.md                     — severity-classified code review
│   └── site-eval.md                  — static site pre-launch audit
├── rules/
│   ├── builder-ethos.md              — six core engineering principles (always on)
│   ├── code-standards.md             — types, comments, patterns (always on)
│   └── static-site-standards.md     — static site architecture and quality (always on)
└── skills/
    ├── architect/                    — system design for complex projects
    ├── autoresearch-review/          — Karpathy-style pre-merge bug analysis
    ├── backend-builder/              — APIs, servers, databases
    ├── browser-extension-builder/   — Chrome/Firefox MV3 extensions
    ├── context-restore/              — session recovery from checkpoint ← NEW
    ├── context-save/                 — session checkpoint ← NEW
    ├── create-issue/                 — issue capture
    ├── createplan/                   — implementation planning
    ├── debug/                        — systematic root-cause tracing
    ├── deploy/                       — deployment and CI/CD
    ├── design-shotgun/               — 4 HTML design directions, pick one ← NEW
    ├── documentation/                — changelog + inline docs
    ├── execute/                      — step-by-step execution
    ├── learn/                        — project brain (.claude/brain.md) ← NEW
    ├── learning/                     — teaching mode
    ├── mobile-app-builder/           — PWA + Expo/React Native
    ├── monitor/                      — post-ship observability
    ├── grill/                        — YC forcing questions before code
    ├── peer-review/                  — triage reviewer feedback
    ├── reflect/                      — self-correction loop
    ├── retro/                        — weekly engineering retrospective ← NEW
    ├── security-review/              — OWASP + threat modeling
    ├── ship/                         — complete release workflow ← NEW
    ├── simplify/                     — code quality and reuse review
    ├── static-site-replicator/       — replicate any reference website
    ├── test-gen/                     — targeted test generation
    └── ui-hunt/                      — find best-in-class UI reference ← NEW

outputs/
└── [project-name]/
    └── index.html
```

---

## What Makes tanker Different from gstack

| Feature | gstack | tanker |
|---------|--------|-------|
| Product thinking before code | `/grill` | `/grill` |
| UI reference research | Manual | `/ui-hunt` — automated, category-specific |
| Design variants | `/design-shotgun` (image mockups) | `/design-shotgun` (working HTML prototypes) |
| Project brain | `/learn` (JSONL) | `/learn` (structured `.claude/brain.md` per project) |
| Session continuity | `/context-save` + `/context-restore` | `/context-save` + `/context-restore` |
| Browser automation | Compiled Chromium binary | N/A (pure Claude Code) |
| Skill chaining | Manual handoffs | Principle 6 in builder-ethos — chaining is enforced |
| Safety guardrails | `/careful`, `/freeze`, `/guard` | Principle 5 in builder-ethos — always on |
| Static site quality gate | N/A | `site-eval` agent mandatory before delivery |
