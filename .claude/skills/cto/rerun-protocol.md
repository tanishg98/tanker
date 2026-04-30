# /cto --rerun-from protocol

> Selective replay from any Message envelope. Built on top of `messages.jsonl` (steal #1) and the subscription pass (steal #8).

## Use cases

- The PRD-reviewer flagged something that was actually fine; you want to redo from `/architect` without redoing the PRD.
- Build phase produced bad backend code; you want to rerun only the backend subagent without re-provisioning.
- A subscription agent (e.g. slack-notifier) failed; you want to replay just its dispatch without re-running the producing skill.

## Invocation

```bash
/cto --rerun-from msg_01HX...
/cto --rerun-from msg_01HX... --only agent:backend-engineer    # rerun a single subscriber
/cto --rerun-from msg_01HX... --skip skill:autoresearch-review # rerun all subscribers EXCEPT this one
```

## Phase 0 — Resolve target

Read `outputs/<slug>/messages.jsonl`. Find the message with `id == <msg_id>`. If not found, STOP with `❌ message id not found in messages.jsonl`.

## Phase 1 — Compute affected phases

Walk forward from the target message:

```python
target = find_msg(msg_id)
target_index = messages.index(target)
forward = messages[target_index:]  # target + everything after
affected_phases = set(m["phase"] for m in forward)
```

## Phase 2 — Snapshot

Before mutating anything:

```bash
cp outputs/<slug>/messages.jsonl  outputs/<slug>/messages.<ts>.jsonl.bak
cp outputs/<slug>/state.json      outputs/<slug>/state.<ts>.json.bak
```

Snapshots are kept indefinitely. They're cheap and the only way to undo a rerun-from gone wrong.

## Phase 3 — Truncate state

Remove forward Messages from `messages.jsonl` (keep target + everything before, drop after target — including target if `--exclusive`). Update `state.json`:

```python
state.phases_done = [p for p in state.phases_done if p not in affected_phases]
state.phase = first_unfinished_phase()
```

## Phase 4 — Replay

Two modes:

**A. Forward-DAG replay (default):** run `/cto --resume <slug>`. The standard resume protocol picks up at `state.phase` and walks the canonical DAG forward. New Messages are written to `messages.jsonl`.

**B. Subscriber-only replay (`--only <id>` / `--skip <id>`):** don't re-run the producing skill. Instead, re-emit the target Message to the subscription pass with the filter applied:

```python
target = find_msg(msg_id)
subscribers = match_subscribers(target)
if --only: subscribers = [s for s in subscribers if s.name == only_target]
if --skip: subscribers = [s for s in subscribers if s.name != skip_target]
for sub in subscribers:
    dispatch(sub, target)
```

This lets you rerun a single subscriber without burning tokens regenerating the artifact.

## Phase 5 — Audit

After replay completes, append a `rerun_report` Message:

```json
{
  "id": "msg_<new>",
  "ts": "<iso>",
  "phase": "rerun",
  "cause_by": "/cto --rerun-from",
  "sent_from": "cto:rerun",
  "send_to": [],
  "artifact_type": "final_report",
  "meta": {
    "rerun_target": "msg_01HX...",
    "phases_replayed": ["architect", "plan", "build"],
    "subscribers_dispatched": ["agent:backend-engineer", "agent:pre-merge"],
    "snapshot_files": ["messages.<ts>.jsonl.bak", "state.<ts>.json.bak"]
  },
  "status": "ok"
}
```

This is what `/cto --audit <slug>` shows in the per-phase table. Reruns are first-class.

## Safety rails

- **Never rerun past a human gate without re-confirming.** If `phases_replayed` includes `prd_human_review` or `mvp_human_review`, force the gate again (don't auto-approve from the prior `human_gates.<gate>.verdict`).
- **Provisioners are idempotent — rerun is safe.** But if a rerun would *destroy* infra (rare, e.g. you targeted a Message before provisioning and replay would regenerate the project), confirm with user before proceeding.
- **Cost cap is re-checked before each replayed phase.** If the cap is hit during replay, halt; subsequent rerun must raise `--max-cost-usd` or wait.
- **Subscription dispatch is still idempotent.** A subscriber that already consumed `msg_id` in the original run does NOT re-fire under `--only` unless you pass `--force`.

## Limitations

- Reruns can't change the past. If PRD content changed in a way that would have led to a different `/architect` output, the rerun produces what the *current* `/architect` does — not what would have happened in an alternate-history run.
- Reruns don't guarantee deterministic LLM output. Even with same input, you may get a different artifact. Compare via `diff` if it matters.

## Implementation note

The `/cto` SKILL.md prompt should call out the `--rerun-from` subcommand in its argument list (already added). The runtime parsing is the orchestrator's job — keep the parser simple, route to the protocol above.
