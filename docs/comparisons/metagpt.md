# Tanker vs MetaGPT

[MetaGPT](https://github.com/FoundationAgents/MetaGPT) is the most popular multi-agent code-generation framework — 40k+ stars, ICLR 2024 paper, Python-first. Tanker borrows MetaGPT's best architectural moves while ending in a different place: a deployed product, not a code repo.

## TL;DR

- **MetaGPT writes code.** Tanker ships products.
- **MetaGPT is fully autonomous.** Tanker has two human gates — pre-qualified by review agents.
- **MetaGPT is generic.** Tanker is opinionated.
- **MetaGPT is multi-provider.** Tanker is Claude Code-native.

If you want a generic Python framework you can drop into any LLM stack, use MetaGPT. If you want an opinionated Claude Code-native pipeline that ends in a deployed URL with monitoring wired, use Tanker.

## Side-by-side

| | MetaGPT | Tanker |
|---|---|---|
| **One-line entry** | `metagpt "build a snake game"` | `/cto "<brief>"` |
| **Roles** | PM, Architect, Engineer, QA (~5) | 34 skills + 9 agents |
| **SOPs** | Hardcoded role prompts | `.claude/skills/*/SKILL.md` + 3 always-on rules |
| **Shared memory** | Environment + Memory objects (per-run) | `.claude/brain.md` + auto-memory + `outputs/<slug>/state.json` (persistent, resumable) |
| **Context retrieval** | None | brain-index (ChromaDB over Obsidian vault) + refs-index (curated GitHub repos) |
| **Human gates** | None — fully autonomous | Two mandatory gates (PRD, MVP), pre-qualified by review agents |
| **Real infra provisioning** | No — produces local code | Yes — gh + supabase + vercel + railway provisioner agents |
| **Quality gates** | One QA agent | pre-merge + autoresearch-review + prd-reviewer + mvp-reviewer + site-eval + security-review |
| **Cross-model peer review** | No | `/advisor` runs Sonnet over Opus output before stakeholder send |
| **Output** | Local code repo | Deployed product (preview URL + prod URL + repo URL + monitoring) |
| **Resumability** | Per-run, ephemeral | `state.json` checkpointed every phase — `/cto --resume <slug>` works across sessions |
| **Cost ceiling** | None | `--max-cost-usd` (default $10) |
| **Audit trail** | Implicit in LLM logs | `messages.jsonl` with typed envelope per artifact |
| **Distribution** | Pip install | Drop `.claude/` into any project |
| **License** | MIT | MIT |

## What Tanker borrows from MetaGPT

Honest credit:

1. **Typed Message schema with provenance** — `cause_by`, `sent_from`, `send_to`, `in_reply_to`. Tanker's [messages.jsonl](../architecture/messages.md) is directly inspired by MetaGPT's `metagpt/schema.py`.
2. **SOP triplet prompt pattern** — Constraints + Reference + Output Format. Tanker's SKILL.md files now follow this rigid pattern, lifted from MetaGPT's `metagpt/actions/write_prd_an.py`.
3. **Bounded review-retry loop** — Tanker's `/cto` Phase 5 caps engineering subagent retries at 2, matching MetaGPT's `WriteCodeReview` loop.
4. **DataInterpreter pattern** — Tanker's `/analyst` skill (Plan → Execute → Reflect → Decide) is modeled on MetaGPT's `metagpt/roles/di/data_interpreter.py`.

## What's different

### 1. Tanker ships products, MetaGPT writes code

MetaGPT's pipeline ends with a repo on disk. Tanker's `/cto` provisions GitHub + Supabase + Vercel + Railway, deploys, smoke-tests, and wires monitoring. Different scope.

### 2. Two human gates, pre-qualified

MetaGPT trusts the agent pipeline end-to-end. Tanker pauses twice — at PRD, at MVP — but only after a review agent has pre-qualified the artifact. The owner sees only what's worth seeing. Total owner attention per `/cto` run: ~30 minutes.

### 3. Taste layer

Tanker's `builder-ethos` rule encodes opinions: an explicit "No AI Slop" ban list, light-mode-only for SMB tools, mobile-first responsive, semantic HTML, IntersectionObserver animations. MetaGPT is taste-agnostic by design.

### 4. Retrieval over personal corpus

`brain-index` indexes your Obsidian vault. `refs-index` indexes curated GitHub repos. `/cto` Phase 1 retrieves from both before any other step. MetaGPT starts every run cold.

### 5. Cross-model peer review

`/advisor` runs Sonnet over Opus output (or vice versa) to catch undefended claims before stakeholder send. MetaGPT has no equivalent hook.

### 6. Cost ceiling

`--max-cost-usd <N>` aborts gracefully when hit. Tanker tracks spend per Message envelope. MetaGPT lets the run go.

## What MetaGPT does better

Honest:

- **Generic + reusable.** MetaGPT works for anyone, any domain. Tanker is opinion-locked.
- **Multi-provider.** OpenAI, Claude, Azure, local — MetaGPT switches via `config2.yaml`. Tanker is Claude Code-native.
- **Published research + community.** ICLR 2024 paper, 40k+ stars, Discord with 10k+ members. Tanker is new.
- **Fully autonomous run.** No gates — better for short tasks where human attention is the bottleneck.
- **Examples directory.** 40+ runnable examples vs Tanker's 5.

## When to use which

**Use MetaGPT if:**
- You want a generic Python framework.
- You're not on Anthropic's stack.
- You want fully autonomous runs.
- You want to study a published research framework.

**Use Tanker if:**
- You're on Claude Code already.
- You want a deployed product, not a repo.
- You want human gates without owner attention burn.
- You have an Obsidian vault or curated reference library you want the autopilot to draw from.
- You want opinionated quality rails baked in.

## Migrating from MetaGPT to Tanker

Concept mapping:

| MetaGPT | Tanker |
|---|---|
| `Role` class | Skill (`.claude/skills/<name>/SKILL.md`) |
| `Action` class | Skill output JSON sidecar (validated by `.claude/schemas/*`) |
| `Environment` | `outputs/<slug>/` directory + `messages.jsonl` |
| `Memory` | `.claude/brain.md` + brain-index (ChromaDB) |
| `SoftwareCompany.investment` | `--max-cost-usd` flag |
| `WriteCodeReview` loop | `/cto` Phase 5 retry loop |
| `DataInterpreter` | `/analyst` skill |

Most MetaGPT pipelines port to Tanker by writing their roles as SKILL.md files and chaining via Tanker's [skill chaining](../rules/builder-ethos.md) principle.
