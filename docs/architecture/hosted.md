# Hosted Tanker (`tanker.dev`) — architecture v0

> Status: **planned, not built.** This page captures the design so when you're ready to ship the hosted product, the architecture is decided.

## Why host

Local Tanker requires: Claude Code, a vault with credentials, an Obsidian vault (optional), brain-index venv. It's friction. A hosted `tanker.dev` lets curious skeptics try `/cto` without installing anything — and converts a fraction of them to power-users who self-host later.

## Tiers

| Tier | What you get | Price |
|---|---|---|
| **Free trial** | One `/cto` run per month, max $5 cost cap, no provisioning (output is a downloadable repo zip) | $0 |
| **Solo** | Unlimited `/cto`, real provisioning to your own GitHub/Vercel/Supabase, $25/mo cost included | $20/mo |
| **Team** | Same + shared workspace + 3 seats + Discord priority | $99/mo |
| **Self-host** | Tanker as today, free MIT, no hosted service | $0 |

The free tier is the conversion engine. It MUST produce something the user wants to share — a downloadable repo + a public preview URL on `*.tanker.dev` subdomain.

## Stack (proposed)

- **Frontend** (`tanker.dev/app/`): Next.js 16 App Router. One-page UI with brief input, real-time event log, gate dialogs.
- **API** (`api.tanker.dev`): FastAPI on Railway. Receives briefs, dispatches background jobs, streams `messages.jsonl` to the frontend via SSE.
- **Worker** (`worker.tanker.dev`): runs the actual `/cto` pipeline. Each run = one Vercel Sandbox microVM (Firecracker) — isolation per-tenant, ephemeral.
- **DB**: Supabase Postgres (multi-tenant, RLS). Tables: `users`, `runs`, `messages` (mirror of `messages.jsonl`), `human_gates`, `billing`.
- **Auth**: Clerk or Supabase Auth.
- **Billing**: Stripe.
- **LLM**: Anthropic API directly (no Claude Code subscription needed for hosted users).
- **Storage**: Vercel Blob for run artifacts (PRDs, plans, screenshots).
- **Queue**: Inngest or BullMQ for /cto pipeline orchestration.

## Run lifecycle

```
user submits brief
  → POST /runs (api)
    → creates run record, returns run_id
    → enqueues "cto.start" job
  → frontend opens SSE on /runs/{id}/events

cto.start job:
  → spawns Vercel Sandbox
  → mounts read-only Tanker .claude/ + tenant credentials
  → runs /cto pipeline, streaming messages.jsonl to API → SSE → frontend
  → at gate: pauses, emits "gate_open" event, stores gate_id
  → user clicks approve/fix/abort → POST /gates/{id}/decision
  → resumes pipeline

cto.complete:
  → if free tier: zip output, upload to Blob, email link
  → if paid tier: provisioning agents fire against tenant's vault credentials
  → final_report stored, billing event recorded
```

## Vault model for hosted

Each tenant has their own vault row in `vaults` table. Provisioner agents read from that row, not from `~/.claude/vault/credentials.json`. The vault columns map 1:1 to the local file:

```sql
create table vaults (
  user_id uuid primary key references users(id),
  github jsonb,        -- {token: "..."}
  vercel jsonb,
  supabase jsonb,
  -- … same as ~/.claude/vault/credentials.json
);
alter table vaults enable row level security;
create policy "users see own vault" on vaults for all using (auth.uid() = user_id);
```

For free trial: tenant has no vault. `/cto` runs in "no-provisioning" mode and outputs only a downloadable zip + public preview URL.

## Sandbox per run

Vercel Sandbox (Firecracker microVM):
- **Read-only mount:** Tanker `.claude/` source from a baked image.
- **Read-write mount:** `outputs/<slug>/` to a per-run blob path.
- **Network:** allowed only to (Anthropic API, GitHub API, Vercel API, Supabase API, Railway API). No general internet.
- **Cap:** 3 hours wall clock, 4GB RAM. Hard kill at limit.

## Cost model

Per `/cto` run:
- LLM: $3-6 (Anthropic API at default `tanker.yaml` distribution)
- Sandbox: $0.10-0.30 (Vercel Sandbox per-run pricing)
- Storage: pennies
- Total cost-of-goods: ~$3.50-6.50

Solo tier ($20/mo) breaks even at ~3-4 runs/month. Most paid users will run 6-12/month → 60-70% gross margin.

Free tier: one run/month with $5 cap → cost-of-goods $5 → loss of $5/free user/month. Acceptable as an acquisition cost.

## Compliance + privacy

- Tenant data isolated per-Sandbox + per-DB tenant.
- LLM prompts are sent to Anthropic; that's the same threat model as local.
- No tenant's brief is used for training (Anthropic API doesn't train on commercial API).
- Tenant can delete all data anytime via dashboard; deletion is hard-delete.
- SOC 2 not required for v0; document threat model + privacy policy clearly.

## Build order (when you're ready)

| Phase | Scope | Estimate (Claude Max + Tanker velocity) |
|---|---|---|
| 1 | Frontend stub, API stub, single-tenant single-user, no Sandbox (run on Railway worker) | 4-6 days |
| 2 | Sandbox isolation, free-tier flow with downloadable zip | 5-7 days |
| 3 | Stripe billing, paid tier with vault, provisioning end-to-end | 6-8 days |
| 4 | Team tier, shared workspace, Discord priority queue | 5-7 days |

Ballpark: 4-5 weeks solo to v0 paid. Use `/cto` itself to build it (good dogfooding).

## Naming the domain

`tanker.dev` is the canonical. Reserve also: `tanker.run`, `gettanker.com`, `tanker.so`. The first is the launch domain; the others are defensive.

## Open questions

- **Free tier abuse:** how to prevent 1000 throwaway emails for $5 LLM credit each. Solutions: GitHub auth required, IP/device fingerprint, rate-limit per-card.
- **Long runs:** /cto can take 3 hours. Frontend needs robust SSE reconnect, mobile push notification when gate opens.
- **Subscriber agents in hosted:** how to let users add custom subscribers without giving them code execution in the worker. Solution: a curated marketplace of subscribers, gated.
- **Self-host migration:** users on Solo who want to switch to self-host should get a one-click "export my vault" + a `tanker self-host` command that pulls their state.
