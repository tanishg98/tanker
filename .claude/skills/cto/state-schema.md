# /cto state.json schema

Every `/cto` run writes to `outputs/<slug>/state.json`. This is the canonical schema. All provisioners and subagents append to it.

```json
{
  "slug": "indian-d2c-dashboard",
  "name": "Indian D2C Dashboard",
  "brief": "AI business analyst for Indian D2C sellers...",
  "started_at": "2026-04-27T14:05:00Z",
  "completed_at": null,
  "mode": "autopilot",
  "phase": "build",
  "phases_done": ["intake", "context", "reference", "grill", "architect", "plan", "advisor", "provision"],
  "budget": {
    "max_cost_usd": 10.0,
    "spent_usd": 1.84,
    "warned_at_70pct": false,
    "halted_budget": false
  },
  "human_gates": {
    "prd": { "verdict": "approved", "feedback_iterations": 0, "approved_at": "2026-04-27T14:42:00Z" },
    "mvp": null
  },
  "decisions": {
    "stack": {
      "frontend": "nextjs-14",
      "backend": "fastapi",
      "db": "supabase-postgres",
      "deploy": { "frontend": "vercel", "backend": "railway" }
    },
    "skipped_benchmark": false,
    "advisor_critical_issues": []
  },
  "infra": {
    "github": {
      "owner": "tanishg98",
      "name": "indian-d2c-dashboard",
      "url": "https://github.com/tanishg98/indian-d2c-dashboard",
      "default_branch": "main",
      "branch_protected": true
    },
    "supabase": {
      "project_ref": "abcdefgh",
      "url": "https://abcdefgh.supabase.co",
      "region": "ap-south-1",
      "vault_path": ".supabase.indian-d2c-dashboard",
      "schema_applied": true,
      "migrations_dir": "supabase/migrations/"
    },
    "vercel": {
      "project_id": "prj_xxx",
      "project_name": "indian-d2c-dashboard",
      "framework": "nextjs",
      "production_url": "https://indian-d2c-dashboard.vercel.app",
      "custom_domain": "d2cos.in"
    },
    "railway": {
      "project_id": "rwy_xxx",
      "service_id": "svc_xxx",
      "url": "https://indian-d2c-dashboard.up.railway.app",
      "healthcheck": "/health",
      "postgres_attached": false
    }
  },
  "build": {
    "subagents_dispatched": ["frontend-engineer", "backend-engineer", "data-engineer", "content-engineer"],
    "prs": {
      "data":     { "url": "...", "merged": true,  "pre_merge_pass": true },
      "backend":  { "url": "...", "merged": true,  "pre_merge_pass": true },
      "frontend": { "url": "...", "merged": false, "pre_merge_pass": null },
      "content":  { "url": "...", "merged": false, "pre_merge_pass": null }
    }
  },
  "deploy": {
    "production_url": "https://d2cos.in",
    "preview_url_pattern": "https://indian-d2c-dashboard-git-{branch}.vercel.app",
    "healthcheck_passing": true,
    "deployed_at": "..."
  },
  "monitoring": {
    "sentry": { "project": "...", "dsn_in_vault": true },
    "plausible": { "domain": "d2cos.in" },
    "uptime": { "provider": "betterstack", "monitor_id": "..." }
  },
  "errors": []
}
```

## Fields

- `phase` — current phase, one of: `intake | context | reference | grill | benchmark | prd | prd_review_agent | prd_human_review | architect | plan | advisor | provision | build | mvp_review_agent | mvp_human_review | deploy | monitor | report | done | halted_budget`
- `phases_done` — append-only list. Resume protocol skips any phase in this list.
- `budget` — `{ "max_cost_usd": float, "spent_usd": float, "warned_at_70pct": bool, "halted_budget": bool }` — orchestrator-enforced cost ceiling. See `message-schema.md` for how `spent_usd` is computed (sum of `cost_usd` across messages.jsonl).
- `human_gates` — `{ "prd": { "verdict": "approved" | "abort" | null, "feedback_iterations": <n>, "approved_at": "..." }, "mvp": { ... } }` — tracks the two HITL gates so resume knows whether the user already approved.
- `errors` — append-only. On failure, push `{ phase, agent, error, ts }`. Don't silently swallow.

## Companion files

Every `outputs/<slug>/` also contains:

- `messages.jsonl` — one Message envelope per line. See `message-schema.md` for the full schema. This is the audit trail; `state.json` is the high-level status.
- `prd/` — PRD bundle (md + html mocks + json schema sidecar)
- `architecture.md`, `plan.md`, `advisor.md`, `reference-brief.md`, `context.md` — phase artifacts referenced by Messages.

## Resume

```bash
/cto --resume indian-d2c-dashboard
```

Reads state.json, finds first phase NOT in `phases_done`, runs from there.

## Status

```bash
/cto --status indian-d2c-dashboard
```

Prints summary table — phase, infra URLs, PR status, errors. Read-only.
