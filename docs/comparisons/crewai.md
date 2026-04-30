# Tanker vs CrewAI

[CrewAI](https://github.com/crewAIInc/crewAI) is a Python framework for orchestrating role-playing autonomous AI agents. Agents have roles, goals, backstories, and collaborate as a "crew."

## TL;DR

- **CrewAI is a role-playing framework.** Tanker is a product-build pipeline.
- **CrewAI is generic.** Tanker is opinionated and deployment-aware.

## Side-by-side

| | CrewAI | Tanker |
|---|---|---|
| **Primary abstraction** | Crew + Agent + Task | Skill + Agent + Rule |
| **Agent definition** | Role + goal + backstory + tools | YAML frontmatter + prompt body + JSON schema |
| **Process model** | Sequential / hierarchical | DAG with HITL gates + bounded retry loops |
| **Memory** | Optional, multiple backends | brain-index (ChromaDB) + per-project brain.md + auto-memory |
| **Deployment** | None | gh + supabase + vercel + railway provisioner agents |
| **Human gates** | None | Two mandatory gates pre-qualified by review agents |
| **Cost tracking** | Token usage in callbacks | `--max-cost-usd` cap + per-Message cost in `messages.jsonl` |
| **Audit trail** | LLM logs | Typed Message envelope per artifact |

## What Tanker borrows from CrewAI

- **Role-as-prompt-contract pattern.** CrewAI's clean role/goal/backstory definition pattern informs Tanker's SKILL.md structure (name + description + triggers + body).

## What's different

- **CrewAI is a kit.** Tanker is an opinionated end-to-end pipeline.
- **CrewAI ends with agent output.** Tanker ends with a deployed URL.
- **Tanker has built-in retrieval.** CrewAI memory is optional and unconfigured by default.

## When to use which

**CrewAI if** you want a Python framework for custom agent crews and you're comfortable wiring deployment + quality + memory yourself.

**Tanker if** you want all of that wired in a Claude Code-native pipeline that ends in a live product.
