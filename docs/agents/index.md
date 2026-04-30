# Agents

Tanker ships 9 agents. Each runs in an isolated context, returns a structured report, and either does read-only analysis or scoped-write provisioning.

## Read-only review agents

| Agent | When to run |
|---|---|
| [explore](./explore.md) | Before planning any feature or bug fix |
| [pre-merge](./pre-merge.md) | Before every PR merge — no exceptions |
| review | On any significant code change |
| [site-eval](./site-eval.md) | After any static site build, before delivery |
| [prd-reviewer](./prd-reviewer.md) | Pre-qualifies PRD before human gate 1 |
| [mvp-reviewer](./mvp-reviewer.md) | Pre-qualifies MVP before human gate 2 |

## Research agent

| Agent | When to run |
|---|---|
| [github-scout](./github-scout.md) | Before `/architect` on any new build |

## Provisioner agents (autopilot infra)

See [Provisioners](../architecture/provisioners.md).

## Skills vs Agents

| | Skills | Agents |
|---|---|---|
| Invoked | `/skill-name` slash command | spawned by Claude via Agent tool |
| Context | current conversation | isolated, fresh |
| File access | read+write | read-only or scoped-write |
| Used for | active building, planning | research, review, pre-launch checks |

Think of it as: **skills are Claude doing work. Agents are Claude dispatching a specialist.**
