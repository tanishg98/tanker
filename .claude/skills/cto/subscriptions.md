# /cto pub-sub Environment

> Inverts the `/cto` orchestrator from a hardcoded DAG into a subscription registry. Agents subscribe to artifact types they care about; the orchestrator emits Messages and routes them to subscribers.

## Why

The original `/cto` SKILL.md hardcoded the DAG (Phase 0 → 1 → 2 → ...). Adding a new agent meant editing the orchestrator. With subscriptions, agents declare what they consume and produce; the orchestrator becomes a loop that reads `messages.jsonl`, finds subscribers for unconsumed messages, dispatches them.

Trade-offs:

- **Pro:** new agents are drop-in. PRs from contributors don't need to touch `/cto` SKILL.md.
- **Pro:** parallel dispatch is automatic — every subscriber for an artifact type fires concurrently.
- **Con:** harder to reason about a single run. The DAG is implicit, not visible.
- **Con:** debugging cycles is harder (A subscribes to B's output, B subscribes to A's output).

For this reason, Tanker keeps the canonical phase order in SKILL.md as a fallback, but allows agents to *also* be subscription-driven for new behaviour. The DAG remains the spine; subscriptions are the extensions.

## The registry

Subscriptions live in `.claude/agents/<name>.md` YAML frontmatter:

```yaml
---
name: backend-engineer
description: Build backend code for /cto Phase 5
tools: Read, Edit, Write, Bash
model: inherit
subscribes_to:
  - { artifact_type: architecture,  cause_by: ["/architect"] }
  - { artifact_type: plan,          cause_by: ["/createplan"] }
publishes:
  - { artifact_type: build_pr, send_to: ["agent:pre-merge"] }
  - { artifact_type: build_pr, send_to: ["skill:autoresearch-review"] }
---
```

`subscribes_to` is a list of filters against `messages.jsonl`. An agent fires when a Message is produced that matches **any** of its subscription clauses AND the agent has not already consumed that message id.

Match rules:
- `artifact_type`: required, exact match.
- `cause_by`: optional list, exact match against the Message's `cause_by`.
- `phase`: optional list, exact match.
- `meta_filter`: optional dict — every key in `meta_filter` must match the Message's `meta` (deep eq).

## Orchestrator loop (additive to the existing DAG)

After the canonical phase has run and written its Message envelopes, the orchestrator does one pass:

```python
# Pseudocode — runs after each phase write
unconsumed = [m for m in messages_jsonl if not m.get("consumed_by")]
for msg in unconsumed:
    matching_agents = []
    for agent in load_agents():  # parses .claude/agents/*.md frontmatter
        for sub in agent.get("subscribes_to", []):
            if matches(sub, msg):
                matching_agents.append(agent.name)
                break
    for agent_name in matching_agents:
        if (agent_name, msg.id) not in dispatched_pairs:
            dispatch(agent_name, msg)
            dispatched_pairs.add((agent_name, msg.id))
            mark_consumed(msg, by=agent_name)
```

Idempotent: if the same agent has already consumed the same message, skip. Tracked in a sidecar `outputs/<slug>/.dispatched.json`.

## When to use subscriptions vs hardcoded dispatch

- **Hardcoded** (in `/cto` SKILL.md): the canonical phases. PRD must come before architect, architect before plan. Order is semantic, not just data-flow.
- **Subscriptions** (in agent frontmatter): cross-cutting concerns. Things like:
  - A `cost-monitor` agent that subscribes to every Message and writes a per-phase ledger (currently inline in `--audit` — could be moved to a subscriber).
  - A `slack-notifier` agent that subscribes to `phase: prd_human_review` and posts to Slack when the gate opens.
  - A `compliance-redactor` agent that subscribes to `artifact_type: build_pr` and runs PII scans before merge.

These don't need to be in `/cto`'s DAG. They subscribe and the orchestrator routes.

## Example: adding a slack-notifier agent

`.claude/agents/slack-notifier.md`:

```yaml
---
name: slack-notifier
description: Posts to Slack when /cto needs human attention
tools: WebFetch
model: claude-haiku-4-5-20251001
subscribes_to:
  - { artifact_type: prd_review, meta_filter: { verdict: "PASS" } }
  - { artifact_type: mvp_review, meta_filter: { verdict: "PASS" } }
publishes:
  - { artifact_type: notification, send_to: ["human:slack"] }
---

You are the slack-notifier. When a review-agent PASSes a gate, post to the configured Slack channel with a one-line summary + the review URL. Read webhook URL from `~/.claude/vault/credentials.json` `.slack.webhook_url`.
```

Drop the file, restart `/cto`. No edit to SKILL.md needed.

## Migration

The canonical `/cto` DAG remains in SKILL.md. Existing agents (pre-merge, prd-reviewer, mvp-reviewer, github-scout, *-provisioner) are dispatched by the DAG — adding `subscribes_to` to their frontmatter is optional and additive.

To migrate one fully (e.g. `pre-merge` becomes subscription-only), remove its hardcoded dispatch from `/cto` SKILL.md Phase 5 and add `subscribes_to: [{ artifact_type: build_pr }]` to its frontmatter. The orchestrator's subscription pass picks it up.

Recommended path: leave existing agents on the DAG. New agents (slack-notifier, cost-monitor, compliance-redactor, design-system-checker, …) ship as subscription-only.

## Future: replay

`/cto --rerun-from <msg_id>` (see `rerun-protocol.md`) interacts cleanly with subscriptions: the rerun replays Messages from the target id forward, and subscribers fire on the replayed Messages just like the original run. This is what makes subscription-driven agents debuggable.
