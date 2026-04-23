# Project Brain — tanker

> Auto-maintained by /learn. Read this before starting any session on this project.
> Last updated: 2026-04-22

---

## Conventions
*How this project does things: naming, file structure, patterns, tech choices.*

- Skills live at `.claude/skills/[name]/SKILL.md` with YAML frontmatter (`name`, `description`, `triggers`, `args`), followed by phases, output format, and rules sections
- Always-on rules live in `.claude/rules/` (builder-ethos, code-standards, static-site-standards)
- Agents live in `.claude/agents/[name].md`
- All skill output goes to `outputs/[project-name]/`
- Every skill ends with a handoff line pointing to the next skill in the chain

---

## Decisions
*Why key choices were made. Prevents re-litigating settled questions.*

- **Kit name is tanker:** Renamed from `my-builder-kit` / `claude-builder-kit` to `tanker` — *Reason: personal parallel to gstack (Garry Tan), repo is `tanishg98/tanker`*
- **Three-layer memory system:** Global `~/.claude/CLAUDE.md` rule auto-reads `.claude/brain.md` + `.claude/context.md` + `.claude/git-state.md` at every session start — *Reason: CLI sessions start blank; CLAUDE.md is the only thing that auto-loads*
- **Stop hook for git-state:** `~/.claude/settings.json` Stop hook runs `sync-memory.sh` async on every turn, writes `.claude/git-state.md` — *Reason: always-current branch/commit without manual /context-save*
- **`/remember inject` is semi-manual:** Injects brain into CLAUDE.md for machines without the global rule — *Reason: requires Claude to summarize brain.md, can't be done in a shell script*
- **Skill chaining via SKILL.md instructions:** Skills end with explicit handoff lines; Claude follows them using the Skill tool — *Reason: no native platform chaining mechanism; instruction-following is the only approach*
- **`/ui-hunt` is tanker's unique differentiator:** Finds best-in-class products before building so designs have a real reference — *Reason: root cause of AI slop is building without a reference*

---

## Pitfalls
*What broke, what was confusing, what not to repeat.*

- **`advisor` skill ambiguity:** TWO advisor skills now exist. Global `~/.claude/skills/advisor` = Claude API Opus+Sonnet pattern for building API apps. Tanker `.claude/skills/advisor/` = cross-model peer review (e.g. Sonnet reviews Opus's PRD). Always confirm which one the user means. Default in tanker sessions = the peer-review one.
- **Never write a PRD for a competitive product without running `/benchmark` first.** Prose teardowns let features slip — they describe each competitor's top-line pitch, not their full feature set. Always produce the exhaustive feature matrix (rows = atomic features, cols = competitors, cells = ✅/❌/⚠️) BEFORE any PRD work. Every PRD feature must map back to a matrix row with ship/defer/skip + reason. Learned the hard way on Shiprocket Visibl — missed auto-competitor-discovery + auto-prompt-synthesis + per-prompt rank history because the teardown was prose, not matrix.
- **When building a product inside a larger org (Shiprocket, etc.), always ask what internal teams are building in the same space BEFORE drafting features.** Large orgs ship in parallel — assume overlap until proven otherwise. The Visibl internal tool at Shiprocket was invisible to external teardown and nearly caused duplicate effort.
- **Cross-model peer review (`/advisor`) is mandatory on any single-model-authored PRD, plan, or spec** before it goes to a stakeholder. One model's blind spots = another model's obvious flags.

---

## Preferences
*How the project owner wants things done. These override defaults.*

- After adding or modifying any skill/rule/agent, always commit and push to `tanishg98/tanker`
- Naming suggestions for this project should be personal — TG / Tanish-inspired (like tanker parallels gstack)
- Keep skill SKILL.md files concise and structured — phases, not walls of text
