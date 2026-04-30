# Provisioner agents

Tanker's `/cto` autopilot uses four provisioner agents to create real infrastructure. Each is scoped to one external service, reads from `~/.claude/vault/credentials.json`, and is idempotent.

| Agent | Service | What it does |
|---|---|---|
| `gh-provisioner` | GitHub | Creates repo, sets branch protection on main, pushes secrets from vault, scaffolds `.gitignore` and CI workflow |
| `supabase-provisioner` | Supabase | Creates project via Management API, scaffolds versioned migrations + RLS, captures keys to vault, pushes secrets to GitHub |
| `vercel-provisioner` | Vercel | Creates project linked to GitHub, pushes env vars from vault, configures custom domain, triggers preview deploy on every PR |
| `railway-provisioner` | Railway | Creates project + service, attaches Postgres if needed, configures healthcheck on `/health`, restart policy ON_FAILURE/3 |

## Idempotency

Every provisioner is safe to re-run on existing infra. They detect existing state via the service's API and reconcile rather than recreate. This is what makes `/cto --resume` safe even after a partial provisioning failure.

## Order

`/cto` Phase 4 dispatches provisioners with this order:

1. `gh-provisioner` first — others need the repo to exist.
2. `supabase-provisioner` — Vercel + Railway both need its keys.
3. `vercel-provisioner` and `railway-provisioner` in parallel.

## Failure

If any provisioner returns `error`, `/cto` STOPs and surfaces the API error verbatim. Don't auto-retry blindly — could be plan limits, name collisions, or quota exhaustion.

## Adding a provisioner

To add (e.g. `fly-provisioner`):

1. Create `.claude/agents/fly-provisioner.md` with the agent prompt.
2. Add Fly token to vault schema in `getting-started/vault.md`.
3. Reference in `/cto` Phase 4 dispatch table.
4. Implement idempotent provisioning — read first, write only on diff.
5. Append `provision_report` Message envelope on completion.

See existing `vercel-provisioner.md` as a template.
