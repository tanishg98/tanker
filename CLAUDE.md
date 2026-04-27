## Active Project Memory
<!-- tanker:remember — auto-updated, do not edit manually -->
<!-- Last updated: 2026-04-27 -->

### What this project is
tanker — Claude Code skill + agent framework (parallel to Garry Tan's gstack). 31 skills (added /benchmark + tanker /advisor), 4 agents, 3 always-on rules, three-layer memory system. Repo: tanishg98/tanker.

### Conventions (apply always)
- Skills at `.claude/skills/[name]/SKILL.md` with YAML frontmatter (name, description, triggers, args)
- Always-on rules in `.claude/rules/` — builder-ethos, code-standards, static-site-standards
- Agents in `.claude/agents/[name].md`
- All skill output goes to `outputs/[project-name]/`
- Every skill ends with a handoff line pointing to the next skill in the chain

### Active work
**Visibl v1 (Shiprocket AI, PIVOTED 2026-04-23):** Shopify App Store distribution (not Shiprocket-seller), agent-driven (12 agents + orchestrator), self-serve + done-for-you modes. 1-week build target. Free for 10–20 design partners month 1. v1 platforms: ChatGPT, Perplexity, Gemini, Google AI Mode. Full PRD v2.2 + 78-feature matrix + Top-10 competitor deep-dive all pushed to Notion under parent 34a360b3ada281e4af6de619ef696f88. Local backups at `~/Documents/notion-export/visibl-*.md`. AthenaHQ = closest competitor. Biggest build risk = multi-account Reddit/Quora aged-account infra — must start account aging parallel to build. **Next:** resolve name collision with Shiprocket's internal Visibl tool, then /architect or direct to build.

**Shiprocket D2C OS V1 (ACTIVE, pivoted from RTO Saver wedge 2026-04-27):** AI business analyst for Indian D2C sellers (₹1–50cr/yr). Connects 6 core SaaS tools (Shopify, Shiprocket, Razorpay, Meta, Interakt, AiSensy), syncs into normalized store, answers business questions in grounded chat. Domain `d2cos.in`. Stack: Next.js 14 on Vercel + FastAPI monolith on Fly.io + Supabase Postgres + Anthropic API (Haiku default, Sonnet eval, Opus escalate). Novel: backend is MCP client toward any SaaS publishing public MCP server. V1 success = ≥3 design partners connect ≥3 apps each, ask ≥5 questions/session, accept answers without cross-checking. V1 free, pricing deferred to V1.1. 2-week solo build target. Outputs: `outputs/d2c-os-v1/architecture.md`, `plan.md`, `runbook.md`. **RTO Saver V1 deprecated** — outputs/rto-saver/ kept for reference only.

**Brain-index + reference library (BUILT 2026-04-27, same PR #1):** Local semantic retrieval over the Obsidian vault at `~/Desktop/Obsidian/Brain/` via ChromaDB at `~/.claude/brain-index/data/`. All embeddings local (chromadb default model `all-MiniLM-L6-v2`, ~80MB), no network during embed/query. Two collections: `brain` (vault chunks) + `refs` (curated GitHub repos via `/cto-add-ref`). Manifest at `~/.claude/references/repos.yaml` (human-editable). `/cto` Phase 1 (context load) now runs semantic retrieval against both collections instead of keyword grep — outputs to `outputs/<slug>/context-brain.md` + `context-refs.md`. `github-scout` Phase 0 consults curated refs as Tier 0 priority before any GitHub-wide search. Setup: run `bash .claude/skills/brain-index/setup.sh` once (creates venv, ~200MB install), then `python .claude/skills/brain-index/index.py` to index vault. Stop-hook recommended for nightly auto-refresh.

**`/cto` autopilot stack (BUILT 2026-04-27, PR #1):** Top-level orchestrator with **human-in-the-loop gates**. Owner is the head of product — autopilot pre-qualifies work via review agents, then STOPS for owner approval at two gates: (1) post-PRD (prd-reviewer agent must PASS first), (2) post-local-build (mvp-reviewer agent must PASS first). Production deploy only happens after both human approvals. `--full-auto` flag exists for skipping gates but not recommended for first run on a new product. Credentials in `~/.claude/vault/credentials.json` (gitignored, 0600). Production rails: preview deploys mandatory, versioned migrations, branch protection, health-check rollback, state.json checkpointed every phase = resumable. PRD output is exhaustive — features mapped to screens, all screen states, lightweight HTML wireframes per screen + landing page. Will dogfood on D2C OS V1.

**CEO Brain (Saahil Goel):** Phase 1+2 done. Phase 3 (CEO query access) NOT YET handed off. Skills to build: vault-query → kb-ingest → smart-compile → ceo-slack-monitor → update-brain → pptx-generator → daily-briefing → eval-runner. Notion doc: 345360b3-ada2-8109-a998-dfaa88617eb7.

**Tanish's own brain:** Vault at ~/Desktop/Obsidian/Brain/. Auto-ingestion pipeline live (WatchPaths + LaunchAgents 10:30am files, 10:35am Gmail). Next: run brain_gmail_setup.sh for Gmail OAuth, validate Soul/ files, expand People/.

### Pitfalls (known landmines)
- **SR Engage already validates WhatsApp→prepaid conversion internally — do NOT re-test that assumption. Killer assumption for RTO Saver is adoption, not channel efficacy.**
- **Don't build RTO Saver on a custom risk model in V1 — ship on SR's existing RTO score. Only build a custom model if accuracy becomes the bottleneck post-launch.**
- **Never write a PRD for a competitive product without `/benchmark` first** — prose teardowns let features slip; matrix doesn't (Visibl incident).
- **Inside a larger org (Shiprocket), ALWAYS ask what internal teams are building in the same space** — Shiprocket's internal Visibl tool was invisible to external teardown, nearly caused duplicate effort.
- **`/advisor` mandatory on any single-model-authored PRD/plan/spec** before stakeholder send.
- **`/advisor` skill ambiguity:** global `~/.claude/skills/advisor` = Claude API Opus+Sonnet pattern; tanker `.claude/skills/advisor` = cross-model peer review. In tanker sessions, default = peer-review one.
- Never `git add .` — stage by filename only (tanker + CEO brain security rule).
- `remember` and `learn` skills must be in `~/.claude/skills/` to appear globally.

### Preferences (owner's explicit instructions)
- After adding/modifying any skill/rule/agent, commit and push to tanishg98/tanker
- Naming should be personal/TG-inspired (tanker parallels gstack)
- Keep SKILL.md files concise — phases, not walls of text
- Owner ships fast — 1-week full-feature v1 is real with Claude Max + tanker, not 6-9 months
- Don't apply cross-model advisor changes over author-model PRDs without explicit approval (owner preferred Opus PRD over Sonnet critique)
<!-- end tanker:remember -->
