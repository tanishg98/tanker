## Active Project Memory
<!-- tanker:remember — auto-updated, do not edit manually -->
<!-- Last updated: 2026-04-29 (Rocketizer technical-fluency walkthrough — 4-layer architecture, agent runtime, MCP-vs-app, 6 production cliffs) -->

### What this project is
tanker — a Claude Code skill + agent framework. 34 skills, 9 agents, 3 always-on rules, three-layer memory system. Repo: tanishg98/tanker.

### Conventions (apply always)
- Skills at `.claude/skills/[name]/SKILL.md` with YAML frontmatter (name, description, triggers, args)
- Always-on rules in `.claude/rules/` — builder-ethos, code-standards, static-site-standards
- Agents in `.claude/agents/[name].md`
- All skill output goes to `outputs/[project-name]/`
- Every skill ends with a handoff line pointing to the next skill in the chain

### Active work
**Visibl v1 (Shiprocket AI, PIVOTED 2026-04-23):** Shopify App Store distribution (not Shiprocket-seller), agent-driven (12 agents + orchestrator), self-serve + done-for-you modes. 1-week build target. Free for 10–20 design partners month 1. v1 platforms: ChatGPT, Perplexity, Gemini, Google AI Mode. Full PRD v2.2 + 78-feature matrix + Top-10 competitor deep-dive all pushed to Notion under parent 34a360b3ada281e4af6de619ef696f88. Local backups at `~/Documents/notion-export/visibl-*.md`. AthenaHQ = closest competitor. Biggest build risk = multi-account Reddit/Quora aged-account infra — must start account aging parallel to build. **Next:** resolve name collision with Shiprocket's internal Visibl tool, then /architect or direct to build.

**Rocketizer V1 (ACTIVE, 14-day sprint kickoff 2026-04-28):** External brand = **Rocketizer** (with z, per rocketizer.ai — Shiprocket's official AI brand). Internal codename remains "d2c os" / repo `~/projects/d2c-os/d2c-os-v1/`. Tagline: "a D2C OS". Public-facing rebrand done in landing page; PDFs use Rocketizer.
- **V1 ship plan: chat + 10 ₹-saving agents in 14 days**, racing Kwik AI. Day 2 builds the shared agent runtime (`Agent` base class with `trigger() · reason() · act()` hooks); days 3–7 ship 10 thin subclasses (~200 LoC each). Floor scenario if Day 7 slips: 5 agents (RTO Saver · Cart Recovery · Weight Disputes · Cash Brief · NDR) still beats Kwik's chat.
- **The 10 V1 agents:** RTO Saver, Cart Recovery, Cash Brief, Ad Pruner, Weight Disputes, NDR Resolution, Inventory Sentinel, WA Support Bot, Review Harvest, Cohort Agent. Total ₹ outcome ~₹7–14L/mo per ₹50L GMV brand. Each agent has trigger/data/action/tier/target ₹ specced in PRD §05.
- **Connector strategy: ride on Shiprocket platform**, don't rebuild. SR already integrates 42 couriers (Delhivery/Bluedart/DTDC/Ekart/Shadowfax/Xpressbees/Ecom/+34), Shopify/Woo/Magento/BigCommerce/OpenCart/Wix, Amazon SP-API + Flipkart marketplaces, Razorpay/Cashfree/Paytm/PhonePe payments, native WA via **Engage** (BSP, pre-provisioned for SR merchants), Checkout (21B+ events), Fulfillment (WMS). ~12 engineer-years saved; V1 connector work = ~3 engineer-weeks.
- **Pricing ladder:** Beta (free, V1 closed) → Solo ₹999 → Growth ₹2,999 → Scale ₹9,999 → **Atlas ₹49,999+** (managed/sales-led). **Custom Build Studio** = consulting tier on top of Atlas (₹5–25L per custom agent, 2-4wk delivery, 70-80% gross margin).
- **Documents (final):** `outputs/d2c-os-v1/prd/Rocketizer-Strategy-v1.pdf` (CEO-facing, 9 sections, big-rupee leak cards) + `Rocketizer-PRD-v1.pdf` (engineering, 13 sections, runtime + `_u` schema specced). Anthropic editorial CSS (Tiempos + Source Serif + clay #cc785c) mirroring `~/Documents/SDN/SDN_Final_v3.html`.
- **Built foundation (still good):** schema + RLS + tenant-leak test 5/5 green; 6 connectors; chat engine with Anthropic tool-use; chat UI with SSE + citations. Auth `AUTH_MODE=demo` for V1.
- **Live preview (post-rebrand):** https://d2cos-pqfp15e79-tanishg98s-projects.vercel.app · Repo `tanishg98/d2c-os` · Anthropic API key still placeholder.
- **Pre-merge advisor (Sonnet) ran 2026-04-28** — surfaced needs: derive ₹ claims, add pricing/Year-1 model, add floor scenario, spec runtime + schema columns, clarify Shiprocket data-access mechanism. All folded into v3 PDFs.
- **Backend deploy still pending:** Railway free-tier slot blocked (visibl + angelic-acceptance projects need cleanup or upgrade).
- **Direct competitor: Kwik AI** (GoKwik's beta, chat-only). Rocketizer V1 differentiator = ten agents + multi-product chains + Shiprocket-platform connector advantage. Pre-existing competitor analysis: Datadrew (post-checkout gap), Triple Whale (dashboard not action).

**Brain-index + reference library (BUILT 2026-04-27, same PR #1):** Local semantic retrieval over the Obsidian vault at `~/Desktop/Obsidian/Brain/` via ChromaDB at `~/.claude/brain-index/data/`. All embeddings local (chromadb default model `all-MiniLM-L6-v2`, ~80MB), no network during embed/query. Two collections: `brain` (vault chunks) + `refs` (curated GitHub repos via `/cto-add-ref`). Manifest at `~/.claude/references/repos.yaml` (human-editable). `/cto` Phase 1 (context load) now runs semantic retrieval against both collections instead of keyword grep — outputs to `outputs/<slug>/context-brain.md` + `context-refs.md`. `github-scout` Phase 0 consults curated refs as Tier 0 priority before any GitHub-wide search. Setup: run `bash .claude/skills/brain-index/setup.sh` once (creates venv, ~200MB install), then `python .claude/skills/brain-index/index.py` to index vault. Stop-hook recommended for nightly auto-refresh.

**`/cto` autopilot stack (BUILT 2026-04-27, PR #1):** Top-level orchestrator with **human-in-the-loop gates**. Owner is the operator running `/cto` — autopilot pre-qualifies work via review agents, then STOPS for owner approval at two gates: (1) post-PRD (prd-reviewer agent must PASS first), (2) post-local-build (mvp-reviewer agent must PASS first). Production deploy only happens after both human approvals. `--full-auto` flag exists for skipping gates but not recommended for first run on a new product. Credentials in `~/.claude/vault/credentials.json` (gitignored, 0600). Production rails: preview deploys mandatory, versioned migrations, branch protection, health-check rollback, state.json checkpointed every phase = resumable. PRD output is exhaustive — features mapped to screens, all screen states, lightweight HTML wireframes per screen + landing page. Will dogfood on D2C OS V1.

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
- **Supabase free-tier direct DB host is IPv6-only.** Use the Session Pooler URL (`aws-0-<region>.pooler.supabase.com:5432`, user `postgres.<project-ref>`). IPv4-routable + supports SQLAlchemy. Direct host 503s from most home networks.
- **Tenant-leak landmine:** Supabase pooler logs in as `postgres` superuser → SUPERUSER bypasses RLS even with FORCE. Backend MUST `SET LOCAL ROLE app_rw` (non-superuser) per-tx in addition to `set_config('rls.merchant_id',…)`. Without the role-switch, RLS is silently inert.
- **Shiprocket `.co` TLD goes through CloudFront → 503 anti-bot.** Always default to `apiv2.shiprocket.in` (AWS ELB direct).
- **Indian SaaS rarely offers OAuth.** Shiprocket / Interakt / AiSensy / WATI = API-key only. 2FA-enabled accounts often can't use email+password login flows. Always offer a token-paste path on Indian-platform connectors.
- **OAuth app registration is one-time per platform, not per-merchant.** D2C OS registers as an "app" with each platform once → every merchant uses that single registered app. Don't conflate "partnership per platform" with "partnership per customer."
- **Don't dark-mode SMB tools.** Linear/Vercel-grade dark reads as "engineering tool" to D2C operators. Triple Whale / Stripe / Mercury light mode is the right reference for Indian D2C ICP. Style follows the user.
- **Rocketizer architecture is 4 layers, agents and chat are SIBLINGS.** Connector → Data Layer (canonical `_u` schema, our DB) → {Chat, Agent runtime}. Chat = human-synchronous; agents = cron/webhook-async. Both share connectors, the data layer, the tool catalog, the idempotency table, and per-customer rate limits. Drawing agents "above" chat leads to the 11x/Artisan failure mode.
- **Don't consume third-party MCPs upstream as a substitute for being an app.** Shopify MCP / etc. = stateless, single-user, no webhooks, curated subset only — wrong-shaped for multi-tenant SaaS. Rocketizer MUST be a real Shopify app. **Forward:** publishing a *Rocketizer MCP server* later (so merchants can chat with their data via Claude Desktop) is the legitimate downstream-distribution use of MCP. Two opposite directions.
- **6 Rocketizer V1 production cliffs (full doc at `~/.claude/projects/-Users-tanishgirotra1-projects-Tanker/memory/project_rocketizer_v1_failure_cliffs.md`):** (1) multi-tenancy/RLS — `SET LOCAL ROLE app_rw` per-tx; (2) token-refresh storms — queue + circuit breakers + dead-letter; (3) idempotency — deterministic `action_id` + UNIQUE constraint; (4) LLM non-determinism — `tool_choice` lock + JSON-schema validation + entity whitelists; (5) webhook security — HMAC on raw bytes + `compare_digest` + replay tolerance; (6) Playwright at scale — avoid in V1. Demos always pass these; prod always fails them. Design in from Day 2.
- **Read/write asymmetry is structural.** Read tools = fire instantly, generous limits. Write tools = idempotent, human-confirm when chat-initiated, schema-locked when agent-initiated, audit-logged, share per-customer rate budget across all agents. Tag tools `kind: "read" | "write"` and gate at backend.

### Preferences (owner's explicit instructions)
- After adding/modifying any skill/rule/agent, commit and push to tanishg98/tanker
- Naming should be personal / TG-inspired
- Keep SKILL.md files concise — phases, not walls of text
- Owner ships fast — 1-week full-feature v1 is real with Claude Max + tanker, not 6-9 months
- Don't apply cross-model advisor changes over author-model PRDs without explicit approval (owner preferred Opus PRD over Sonnet critique)
- **External brand for the consumer-facing product = Rocketizer (with z).** Internal codename = d2c os. Repo, engineering channels, codebase use d2c os. Public docs, landing pages, marketing use Rocketizer.
- **CEO-facing docs use Anthropic editorial CSS** mirroring `~/Documents/SDN/SDN_Final_v3.html` — Tiempos Headline + Source Serif body + clay accent #cc785c on cream #faf9f6. Render via headless Chrome `--print-to-pdf`.
- **Run /advisor (cross-model peer review) before sending any single-model-authored PRD/strategy to Saahil or external stakeholders.** Sonnet reads what Opus wrote → catches undefended claims, missing pricing/team asks, fabricated-feeling TAM.
- **Visual leak/money sections beat tables for CEO docs.** Big rupee figures in card grids land harder than rows of prose.
- **When owner asks technical questions, default to 3-level explanations.** Level 1 = plain technical language a non-engineering PM can follow (mental model + diagram). Level 2 = real engineering (code sketches, file structure, the actual loop). Level 3 = where it breaks in production (failure modes, security cliffs). Owner is non-engineering — goal is fluency to read engineers' code and catch corner-cutting. End deep-dives with a one-line offer of the next layer or actionable artifact.
- **When owner shares a mental model and asks "where am I wrong?" — be surgical and honest.** Lead with what they got right (calibration), then call out subtle errors (wrong-shaped framings that lead to wrong design), then list things missed entirely. Don't soften — the value is converting an 80%-right model to a 100%-right one.
<!-- end tanker:remember -->
