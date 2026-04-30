# state.json

The high-level status file for a `/cto` run. Lives at `outputs/<slug>/state.json`. Companion to `messages.jsonl` (the detailed audit trail).

> Canonical reference: `.claude/skills/cto/state-schema.md`.

## Shape

```json
{
  "slug": "indian-d2c-dashboard",
  "name": "Indian D2C Dashboard",
  "brief": "AI business analyst for Indian D2C sellers...",
  "started_at": "2026-04-27T14:05:00Z",
  "completed_at": null,
  "mode": "autopilot",
  "phase": "build",
  "phases_done": ["intake", "context", "reference", "grill", "prd", "prd_human_review", "architect", "plan", "advisor", "provision"],
  "budget": { "max_cost_usd": 10.0, "spent_usd": 1.84, "warned_at_70pct": false, "halted_budget": false },
  "human_gates": {
    "prd": { "verdict": "approved", "feedback_iterations": 0, "approved_at": "2026-04-27T14:42:00Z" },
    "mvp": null
  },
  "decisions": { "stack": { "frontend": "nextjs-14", "backend": "fastapi", "db": "supabase-postgres" } },
  "infra": { "github": { "url": "..." }, "supabase": { "..." }, "vercel": { "..." }, "railway": { "..." } },
  "deploy": {},
  "monitoring": {},
  "errors": []
}
```

## Resume protocol

`/cto --resume <slug>` reads `state.json`, finds the first phase NOT in `phases_done`, and runs from there. Idempotent provisioners + healthcheck-gated rollback make this safe.

## Status

`/cto --status <slug>` prints a summary table — read-only.
