# Message schema

> See `.claude/skills/cto/message-schema.md` for the canonical reference.

Every artifact produced during a `/cto` run is wrapped in a typed Message envelope and appended to `outputs/<slug>/messages.jsonl` (one JSON object per line).

This is what MetaGPT does well. Tanker steals it.

## Why

Without provenance:

- You can't replay a run from a specific point.
- Review agents have to re-parse markdown to recover what skill produced what.
- Cost tracking is impossible.
- Audits require grepping prose.

With Message envelopes:

- `cause_by` tells you which skill produced the artifact.
- `sent_from` / `send_to` capture handoffs.
- `in_reply_to` builds the chain.
- `cost_usd` per Message gives you the per-phase cost table from `--audit`.

## Envelope

```json
{
  "id": "msg_01HX...",
  "ts": "2026-04-30T11:14:02Z",
  "phase": "prd",
  "cause_by": "/prd",
  "sent_from": "skill:prd",
  "send_to": ["agent:prd-reviewer", "human:gate-1"],
  "artifact_type": "prd_bundle",
  "artifact_path": "outputs/<slug>/prd/prd.md",
  "artifact_companion_paths": [
    "outputs/<slug>/prd/index.html",
    "outputs/<slug>/prd/prd.json"
  ],
  "in_reply_to": "msg_01HW...",
  "tokens_in": 8421,
  "tokens_out": 12044,
  "cost_usd": 0.193,
  "status": "ok"
}
```

Validated by [`.claude/schemas/message.schema.json`](https://github.com/tanishg98/tanker/blob/main/.claude/schemas/message.schema.json).

## Querying

```bash
# Everything produced by /prd
jq 'select(.cause_by == "/prd")' outputs/<slug>/messages.jsonl

# What did the prd-reviewer agent see?
jq 'select(.send_to[]? == "agent:prd-reviewer")' outputs/<slug>/messages.jsonl

# Cost per phase
jq -s 'group_by(.phase) | map({
  phase: .[0].phase,
  msgs: length,
  cost_usd: (map(.cost_usd // 0) | add)
})' outputs/<slug>/messages.jsonl

# Build the chain that led to a specific PR
jq 'select(.artifact_type == "build_pr")' outputs/<slug>/messages.jsonl
```

## Selective re-run (planned)

Future: `/cto --rerun-from <msg_id>` will truncate `phases_done` to the phase before that message and restart. Today, `/cto --resume <slug>` resumes from the next incomplete phase using `phases_done` only.
