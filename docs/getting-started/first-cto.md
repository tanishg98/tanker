# First `/cto` run

The fastest way to feel what Tanker does is to run `/cto` against a small brief.

## Pre-flight

```bash
/vault-add github vercel supabase anthropic
```

Each command prompts for the value, writes to `~/.claude/vault/credentials.json` with 0600 perms, and never echoes the value back.

You need at minimum: `anthropic` (for the LLM), `github` (for the repo), and one deploy target. For a fully end-to-end run: all four above.

## Run

```bash
/cto "todo app with email + password auth, magic link, and a simple kanban view"
```

What happens:

1. **Intake.** Slug derived: `todo-magic-kanban`. `outputs/<slug>/state.json` and `messages.jsonl` created.
2. **Context load.** Brain-index + refs queried in parallel.
3. **Reference scan.** `github-scout` finds prior art.
4. **Decision gates.** `/grill` → `/prd` → `prd-reviewer` → 🛑 Gate 1.

You'll see:

```
✋ PRD ready for review
Open: outputs/todo-magic-kanban/prd/index.html
Read: outputs/todo-magic-kanban/prd/prd.md

prd-reviewer verdict: PASS

When you're done reviewing, reply with one of:
  "approved"             — proceed to /architect and the build
  "fix: <feedback>"      — re-run /prd with this feedback, retry the gate
  "abort"                — stop /cto, keep state.json for resume later
```

Open the HTML wireframes in a browser, scroll the markdown PRD, and reply.

5. **Architect → plan → advisor.** Cross-model peer review surfaces undefended claims.
6. **Provisioning.** GitHub repo, Supabase project, Vercel project, Railway service — parallel.
7. **Build.** Frontend + backend + data + content engineers in parallel. Pre-merge + autoresearch on each PR. Bounded retries on `BLOCK`/`PASS_WITH_FIXES`.
8. **Local MVP review.** Server starts at `localhost:3000`. `mvp-reviewer` walks every screen + state. Then 🛑 Gate 2.
9. **Deploy.** Production deploys verified, smoke-tested.
10. **Monitor.** Sentry + analytics + uptime wired.
11. **Final report.** URLs printed.

## Total time

- Owner attention: ~30 minutes (two reviews).
- Wall clock: ~3 hours for a small product.
- Cost: ~$3–6 with default settings (cap at $10 unless you raise).

## Resume after a break

```bash
/cto --resume todo-magic-kanban
```

Picks up exactly where you left off, reading `phases_done` from `state.json`.

## See cost

```bash
/cto --audit todo-magic-kanban
```

Per-phase token + cost breakdown.

## Next

- [Vault & credentials](./vault.md)
- [Brain index](./brain-index.md)
- [Comparisons](../comparisons/metagpt.md)
