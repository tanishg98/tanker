# Project Brain — tanker

> Auto-maintained by /learn. Read this before starting any session on this project.
> Last updated: 2026-04-27

---

## Conventions
*How this project does things: naming, file structure, patterns, tech choices.*

- Skills live at `.claude/skills/[name]/SKILL.md` with YAML frontmatter (`name`, `description`, `triggers`, `args`), followed by phases, output format, and rules sections
- Always-on rules live in `.claude/rules/` (builder-ethos, code-standards, static-site-standards)
- Agents live in `.claude/agents/[name].md`
- All skill output goes to `outputs/[project-name]/`
- Every skill ends with a handoff line pointing to the next skill in the chain
- Autopilot is the orchestrator layer — `/cto` runs the manual chain end-to-end, dispatching skills + provisioner subagents in parallel
- Provisioner agents (gh, supabase, vercel, railway) hit each platform's REST/GraphQL API directly — no CLI dependencies. One agent per service.
- All credentials live at `~/.claude/vault/credentials.json` (0700 dir, 0600 file). Never logged, never echoed, never in commits. Provisioners read with `jq`.
- Per-project state at `outputs/<slug>/state.json`. Every `/cto` phase appends to `phases_done` so any session can `/cto --resume <slug>`.
- Local semantic retrieval over the Obsidian vault via ChromaDB at `~/.claude/brain-index/data/`. All embeddings local (chromadb default model). Two collections: `brain` (vault) + `refs` (curated GitHub repos). Manifest at `~/.claude/references/repos.yaml`.
- `/cto` Phase 1 (context load) calls `python query.py "<keywords>" --collection brain` and `--collection refs`. github-scout Phase 0 consults curated refs as Tier 0 priority before any GitHub-wide search.

---

## Decisions
*Why key choices were made. Prevents re-litigating settled questions.*

- **Kit name is tanker:** Renamed from `my-builder-kit` / `claude-builder-kit` to `tanker` — *Reason: personal parallel to gstack (Garry Tan), repo is `tanishg98/tanker`*
- **Three-layer memory system:** Global `~/.claude/CLAUDE.md` rule auto-reads `.claude/brain.md` + `.claude/context.md` + `.claude/git-state.md` at every session start — *Reason: CLI sessions start blank; CLAUDE.md is the only thing that auto-loads*
- **Stop hook for git-state:** `~/.claude/settings.json` Stop hook runs `sync-memory.sh` async on every turn, writes `.claude/git-state.md` — *Reason: always-current branch/commit without manual /context-save*
- **`/remember inject` is semi-manual:** Injects brain into CLAUDE.md for machines without the global rule — *Reason: requires Claude to summarize brain.md, can't be done in a shell script*
- **Skill chaining via SKILL.md instructions:** Skills end with explicit handoff lines; Claude follows them using the Skill tool — *Reason: no native platform chaining mechanism; instruction-following is the only approach*
- **`/ui-hunt` is tanker's unique differentiator:** Finds best-in-class products before building so designs have a real reference — *Reason: root cause of AI slop is building without a reference*
- **Autopilot defaults to HITL, not full-auto:** `/cto` STOPs at two human-review gates (post-PRD, post-local-MVP) by default. Owner is the head of product. `--full-auto` exists as an explicit opt-out. *Reason: agents pre-qualify the work, owner reviews complete artifacts at the right moments — full-auto is reserved for throwaway prototypes.*
- **Production-grade autopilot rails are architectural, not behavioral:** branch protection on main (gh-provisioner), versioned migrations only (supabase-provisioner), mandatory preview deploys (vercel-provisioner), healthcheck rollback (railway/vercel), state.json checkpointing every phase. *Reason: "stop and ask" is brittle; reversible-by-design is robust.*
- **Local embeddings, not API:** brain-index uses chromadb default model (`all-MiniLM-L6-v2`, ~80MB CPU-only). *Reason: vault is private; embedding it through any external API contradicts the privacy posture of the vault itself.*
- **Curated refs > generic GitHub search:** `/cto-add-ref` lets owner curate repos worth pulling patterns from. github-scout consults this Tier 0 before wider search. *Reason: training-time GitHub priors are stale; owner's curated taste is current and personal.*

---

## Pitfalls
*What broke, what was confusing, what not to repeat.*

- **`advisor` skill ambiguity:** TWO advisor skills now exist. Global `~/.claude/skills/advisor` = Claude API Opus+Sonnet pattern for building API apps. Tanker `.claude/skills/advisor/` = cross-model peer review (e.g. Sonnet reviews Opus's PRD). Always confirm which one the user means. Default in tanker sessions = the peer-review one.
- **Never write a PRD for a competitive product without running `/benchmark` first.** Prose teardowns let features slip — they describe each competitor's top-line pitch, not their full feature set. Always produce the exhaustive feature matrix (rows = atomic features, cols = competitors, cells = ✅/❌/⚠️) BEFORE any PRD work. Every PRD feature must map back to a matrix row with ship/defer/skip + reason. Learned the hard way on Shiprocket Visibl — missed auto-competitor-discovery + auto-prompt-synthesis + per-prompt rank history because the teardown was prose, not matrix.
- **When building a product inside a larger org (Shiprocket, etc.), always ask what internal teams are building in the same space BEFORE drafting features.** Large orgs ship in parallel — assume overlap until proven otherwise. The Visibl internal tool at Shiprocket was invisible to external teardown and nearly caused duplicate effort.
- **Cross-model peer review (`/advisor`) is mandatory on any single-model-authored PRD, plan, or spec** before it goes to a stakeholder. One model's blind spots = another model's obvious flags.
- **Don't push directly to main on the tanker repo.** Sandbox blocks it (correctly — it matches the branch-protection rail we just built). Always work on a feature branch + PR. Local `main` should be force-reset to `origin/main` after committing if you accidentally landed on local main.
- **chromadb install is ~200MB.** First-run brain-index setup downloads the embedding model. Don't auto-install on someone else's machine without explicit consent — trigger only on `/brain-index` invocation.
- **PRD without screen states ≠ a PRD.** prd-reviewer auto-BLOCKs any PRD where a screen has fewer than 4 states (empty/loading/populated/error). Single-state screens are the most common failure mode.

---

## Preferences
*How the project owner wants things done. These override defaults.*

- After adding or modifying any skill/rule/agent, always commit and push to `tanishg98/tanker`
- Naming suggestions for this project should be personal — TG / Tanish-inspired (like tanker parallels gstack)
- Keep skill SKILL.md files concise and structured — phases, not walls of text
- Stage files explicitly by name when committing — never `git add .` (security rule, prevents accidental .env / credential leaks)
- Don't auto-apply cross-model `/advisor` changes over author-model output without explicit owner approval (owner preferred Opus PRD over Sonnet critique on a past run)
- Owner ships fast — 1-week full-feature v1 is real with Claude Max + tanker, not 6–9 months. Plan accordingly; if a build looks like 6 weeks of effort, the architecture is wrong.
