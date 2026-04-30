# Tanker Message Schema

Every artifact produced during a `/cto` run is wrapped in a typed Message envelope. This makes the run **replayable, auditable, and selectively re-runnable.** No more grepping `outputs/<slug>/` to figure out which skill produced what.

## Why

Without provenance metadata, multi-agent runs are unreplayable: review agents have to re-parse markdown to recover which skill produced which artifact, cost tracking is impossible, and selective re-runs require manual surgery. The `cause_by` / `sent_from` / `send_to` envelope fixes all three at once — every artifact carries who produced it, who it was for, and what it replied to.

## The envelope

Every artifact (PRD, architecture doc, plan, advisor review, build PR, mvp review, deploy report) is appended to `outputs/<slug>/messages.jsonl` as one line:

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
  "artifact_companion_paths": ["outputs/<slug>/prd/index.html", "outputs/<slug>/prd/prd.json"],
  "in_reply_to": "msg_01HW...",
  "tokens_in": 8421,
  "tokens_out": 12044,
  "cost_usd": 0.193,
  "status": "ok"
}
```

### Field reference

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | ULID. Generate with `python -c "import ulid; print(ulid.new())"` or `date +%s%N` fallback |
| `ts` | ISO8601 string | yes | UTC, second-precision is fine |
| `phase` | enum | yes | One of the `phase` values in `state-schema.md` |
| `cause_by` | string | yes | Slash command or skill name. e.g. `/prd`, `/architect`, `cto:phase4` |
| `sent_from` | string | yes | Producer ID. Format: `skill:<name>` / `agent:<name>` / `cto:phase<n>` / `human:<gate>` |
| `send_to` | string[] | yes | Intended consumers. Same format as `sent_from`. Multiple OK. |
| `artifact_type` | enum | yes | See artifact_type table below |
| `artifact_path` | string | yes when artifact exists on disk | Relative to repo root |
| `artifact_companion_paths` | string[] | no | Sibling files (HTML mock alongside MD, JSON schema alongside markdown) |
| `in_reply_to` | string | no | Parent message ID. Set when this message is a response to another. |
| `tokens_in` | int | no | Best effort |
| `tokens_out` | int | no | Best effort |
| `cost_usd` | float | no | Used by budget cap |
| `status` | enum | yes | `ok` / `block` / `pass_with_fixes` / `error` |
| `error` | string | no | Set when `status: error`. One-line summary. |
| `meta` | object | no | Free-form. Use sparingly. |

### `artifact_type` enum

```
brief
context_brain
context_refs
reference_brief
grill
benchmark
prd_bundle
prd_review
architecture
plan
advisor_review
provision_report
build_pr
pre_merge_review
autoresearch_review
mvp_review
deploy_report
monitor_report
final_report
```

If you need a new type, add it here AND in the schema. Don't invent types ad-hoc.

## How `/cto` uses it

After every phase, `/cto` (or the dispatched skill/agent on its behalf) appends a Message to `messages.jsonl`. The `state.json` `phase` and `phases_done` keep the high-level status; `messages.jsonl` is the detailed log.

```bash
# Pseudocode for the appender (used by /cto and child skills)
append_message() {
  local payload="$1"
  echo "$payload" >> "outputs/${SLUG}/messages.jsonl"
}
```

## Replay

To re-run from any point:

```bash
# See everything
cat outputs/<slug>/messages.jsonl | jq .

# Show only messages produced by /prd
cat outputs/<slug>/messages.jsonl | jq 'select(.cause_by == "/prd")'

# Show what the prd-reviewer agent consumed
cat outputs/<slug>/messages.jsonl | jq 'select(.send_to[]? == "agent:prd-reviewer")'

# Reconstruct the build chain that led to a specific PR
cat outputs/<slug>/messages.jsonl | jq 'select(.artifact_type == "build_pr")' | jq -r .in_reply_to | xargs -I{} jq "select(.id == \"{}\")" outputs/<slug>/messages.jsonl
```

## Selective re-run

`/cto --rerun-from msg_01HX...` (future: not yet wired) will:
1. Read messages.jsonl
2. Find the target message
3. Truncate `phases_done` back to the phase before that message
4. Restart from the corresponding phase

Until then, `--resume <slug>` resumes from the next incomplete phase using `phases_done` only — same as today.

## Audit & cost

`/cto --audit <slug>` (future) prints:

```
Phase            Messages   Tokens In   Tokens Out   Cost USD
intake                  1          —            —       0.00
context                 4      12,004       1,830       0.04
reference               1      18,200       6,400       0.18
grill                   1       4,210       2,901       0.05
prd                     2      32,000      28,400       0.61
prd_review_agent        1      18,400       4,200       0.16
prd_human_review        1           —            —       0.00
architect               1      14,200      11,000       0.27
...                                                          
Total                  47   1,043,210     408,201       4.92
```

This feeds the budget cap (`--max-cost-usd`).

## Compatibility

Existing `state.json` is unchanged. Messages are additive — old runs without `messages.jsonl` still resume correctly via `phases_done`.

For new runs, both files are produced. `state.json` for high-level status, `messages.jsonl` for the audit trail.
