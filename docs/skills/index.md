# Skills

Tanker ships 34 skills. Each is a slash command in Claude Code that does work in the current conversation.

## The product-build chain

```
/grill → /benchmark? → /ui-hunt → /design-shotgun → /architect → /createplan → /execute → /autoresearch-review → /ship → /deploy → /monitor → /retro
```

Or, autopilot: `/cto "<brief>"`.

## By category

### Autopilot
- [/cto](./cto.md) — orchestrator with HITL gates
- /vault-add — add credentials

### Product & Strategy
- [/grill](./grill.md) — YC-style forcing questions
- [/benchmark](./benchmark.md) — competitor matrix
- [/prd](./prd.md) — exhaustive PRD with HTML wireframes
- /ui-hunt — find best-in-class refs

### Design
- /design-shotgun — 4 working HTML directions
- /static-site-replicator — replicate any reference site

### Planning & Execution
- [/architect](./architect.md) — system design
- [/createplan](./createplan.md) — implementation plan
- [/execute](./execute.md) — step-by-step execution

### Building
- /backend-builder — APIs, servers, databases
- /browser-extension-builder — Chrome/Firefox MV3
- /mobile-app-builder — PWA + Expo/React Native
- [/deploy](./deploy.md) — Vercel/Railway/Fly/Docker
- [/monitor](./monitor.md) — Sentry/Plausible/Better Stack

### Data
- [/analyst](./analyst.md) — Python sandbox + ReAct loop

### Release
- [/ship](./ship.md) — sync, test, push, PR

### Quality
- /autoresearch-review — Karpathy-style bug analysis
- /debug — systematic root-cause tracing
- /test-gen — targeted tests
- /security-review — OWASP + threat modeling
- /peer-review — triage reviewer feedback
- /simplify — code quality + reuse

### Self-improvement
- /reflect — self-correction
- [/retro](./retro.md) — weekly retrospective

### Memory
- [/learn](./learn.md) — `.claude/brain.md` per project
- /context-save — session checkpoint
- /context-restore — session recovery

### Retrieval
- /brain-index — index Obsidian vault to ChromaDB
- /cto-add-ref — curate GitHub references

### Utility
- /create-issue — capture bug/feature
- /documentation — update CHANGELOG + docs
- /learning — three-level explanation
