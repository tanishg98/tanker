# Project Brain — tanker

> Framework-level conventions, decisions, pitfalls, preferences. This file is tracked and public — anything project-specific or sensitive lives in `.claude/brain.private.md` (gitignored).

---

## Conventions
*How this project does things: naming, file structure, patterns, tech choices.*

- Skills live at `.claude/skills/[name]/SKILL.md` with YAML frontmatter (`name`, `description`, `triggers`, `args`), followed by phases, output format, and rules sections
- Always-on rules live in `.claude/rules/` (builder-ethos, code-standards, static-site-standards, claude-executes)
- Agents live in `.claude/agents/[name].md`
- All skill output goes to `outputs/[project-name]/` (gitignored — local-only working artifacts)
- Every skill ends with a handoff line pointing to the next skill in the chain
- Autopilot is the orchestrator layer — `/cto` runs the manual chain end-to-end, dispatching skills + provisioner subagents in parallel
- Provisioner agents (gh, supabase, vercel, railway) hit each platform's REST/GraphQL API directly — no CLI dependencies. One agent per service.
- All credentials live at `~/.claude/vault/credentials.json` (0700 dir, 0600 file). Never logged, never echoed, never in commits. Provisioners read with `jq`.
- Per-project state at `outputs/<slug>/state.json`. Every `/cto` phase appends to `phases_done` so any session can `/cto --resume <slug>`.
- Local semantic retrieval over the owner's knowledge vault via ChromaDB at `~/.claude/brain-index/data/`. All embeddings local (chromadb default model, `all-MiniLM-L6-v2`). Two collections: `brain` (vault) + `refs` (curated GitHub repos). Manifest at `~/.claude/references/repos.yaml`.
- `/cto` Phase 1 (context load) calls `python query.py "<keywords>" --collection brain` and `--collection refs`. github-scout Phase 0 consults curated refs as Tier 0 priority before any GitHub-wide search.

---

## Decisions
*Why key choices were made. Prevents re-litigating settled questions.*

- **Kit name is tanker:** Renamed from `my-builder-kit` / `claude-builder-kit` to `tanker`. *Reason: personal naming convention; repo is `tanishg98/tanker`.*
- **Three-layer memory system:** Global `~/.claude/CLAUDE.md` rule auto-reads `.claude/brain.md` + `.claude/brain.private.md` + `.claude/context.md` + `.claude/git-state.md` at every session start. *Reason: CLI sessions start blank; the global rule is the only thing that auto-loads.*
- **Public/private brain split:** `brain.md` is tracked + framework-only. `brain.private.md` is gitignored + holds project-specific context. *Reason: tanker is a public framework repo; project memory must not contaminate it.*
- **Stop hook for git-state:** `~/.claude/settings.json` Stop hook runs `sync-memory.sh` async on every turn, writes `.claude/git-state.md`. *Reason: always-current branch/commit without manual `/context-save`.*
- **`/remember inject` is semi-manual:** Injects brain summary into CLAUDE.md for machines without the global rule. *Reason: requires Claude to summarize brain.md, can't be done in a shell script.*
- **Skill chaining via SKILL.md instructions:** Skills end with explicit handoff lines; Claude follows them using the Skill tool. *Reason: no native platform chaining mechanism; instruction-following is the only approach.*
- **`/ui-hunt` is tanker's unique differentiator:** Finds best-in-class products before building so designs have a real reference. *Reason: root cause of AI slop is building without a reference.*
- **Autopilot defaults to HITL, not full-auto:** `/cto` STOPs at two human-review gates (post-PRD, post-local-MVP) by default. `--full-auto` exists as an explicit opt-out. *Reason: agents pre-qualify the work, owner reviews complete artifacts at the right moments — full-auto is reserved for throwaway prototypes.*
- **Production-grade autopilot rails are architectural, not behavioral:** branch protection on main (gh-provisioner), versioned migrations only (supabase-provisioner), mandatory preview deploys (vercel-provisioner), healthcheck rollback (railway/vercel), state.json checkpointing every phase. *Reason: "stop and ask" is brittle; reversible-by-design is robust.*
- **Local embeddings, not API:** brain-index uses chromadb default model (`all-MiniLM-L6-v2`, ~80MB CPU-only). *Reason: vault is private; embedding it through any external API contradicts the privacy posture of the vault itself.*
- **Curated refs > generic GitHub search:** `/cto-add-ref` lets owner curate repos worth pulling patterns from. github-scout consults this Tier 0 before wider search. *Reason: training-time GitHub priors are stale; owner's curated taste is current and personal.*

---

## Pitfalls
*What broke, what was confusing, what not to repeat.*

- **`advisor` skill ambiguity:** TWO advisor skills now exist. Global `~/.claude/skills/advisor` = Claude API Opus+Sonnet pattern for building API apps. Tanker `.claude/skills/advisor/` = cross-model peer review (e.g. Sonnet reviews Opus's PRD). Always confirm which one the user means. Default in tanker sessions = the peer-review one.
- **Cross-model peer review (`/advisor`) is mandatory on any single-model-authored PRD, plan, or spec** before it goes to a stakeholder. One model's blind spots = another model's obvious flags.
- **Don't push directly to main on the tanker repo.** Sandbox blocks it (correctly — it matches the branch-protection rail we built). Always work on a feature branch + PR. Local `main` should be force-reset to `origin/main` after committing if you accidentally landed on local main.
- **chromadb install is ~200MB.** First-run brain-index setup downloads the embedding model. Don't auto-install on someone else's machine without explicit consent — trigger only on `/brain-index` invocation.
- **PRD without screen states ≠ a PRD.** prd-reviewer auto-BLOCKs any PRD where a screen has fewer than 4 states (empty/loading/populated/error). Single-state screens are the most common failure mode.
- **Never commit project-specific content to `brain.md` or tracked files.** `brain.private.md` exists for that. Anything that names a company/product/person/customer/CEO/competitor/internal-team belongs in `brain.private.md` only.

---

## Preferences
*How the project owner wants things done. These override defaults.*

- After adding or modifying any skill/rule/agent, always commit (on a feature branch) and push to `tanishg98/tanker`
- Naming suggestions for this project should be personal — TG / Tanish-inspired
- Keep skill SKILL.md files concise and structured — phases, not walls of text
- Stage files explicitly by name when committing — never `git add .` (prevents accidental .env / credential leaks)
- Don't auto-apply cross-model `/advisor` changes over author-model output without explicit owner approval
- Owner ships fast — 1-week full-feature v1 is real with Claude Max + tanker, not 6–9 months. Plan accordingly; if a build looks like 6 weeks of effort, the architecture is wrong.
- **When owner asks technical questions, default to 3-level explanations.** Level 1 = plain technical language a non-engineering PM can follow (mental model + diagram). Level 2 = real engineering (code sketches, file structure, the actual loop). Level 3 = where it breaks in production (failure modes, security cliffs, vocabulary fixes). End deep-dives by offering the next layer or actionable artifact — let owner pick.
- **When owner shares a mental model and asks "where am I wrong?" — be surgical and honest.** Lead with what they got right (calibration), then call out subtle errors (wrong-shaped framings that lead to wrong design), then list things missed entirely. Don't soften.
