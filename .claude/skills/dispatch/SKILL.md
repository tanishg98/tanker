---
name: dispatch
description: Spawn a fresh-context `claude -p` worker to do focused research, exploration, or reading work without bloating the main session's context window. Different from /swarm (which is N parallel code-writing workers in worktrees). Dispatch is 1-to-N read-only researchers that return concise reports. Use when you need an answer that requires reading many files / docs / URLs and you don't want all of that to land in the parent session's context.
argument-hint: "<question or task description>  [--n <workers>] [--model sonnet|opus|haiku] [--max-tokens <N>]"
---

# /dispatch — Fresh-Context Workers

You are using **Dispatch**. You spawn one or more headless `claude -p` workers that each run in a clean context, do focused read-only work, and return a tight report. The parent session never sees the raw exploration — only the synthesis.

This is Tanker's answer to context bloat. The parent session stays sharp; the messy reading happens elsewhere.

Inspired by bassimeledath/dispatch and similar fresh-context patterns. Different from `/swarm`:

| | /dispatch | /swarm |
|---|---|---|
| Purpose | research / read | code / write |
| Workers | typically 1, up to N | N (default 5) |
| Output | markdown report to stdout | branches / PRs |
| Isolation | fresh context only | fresh context + git worktree |
| Permission mode | `plan` (read-only) | `acceptEdits` |

---

## When dispatch fits

- "What does this 800-line file actually do?" → 1 dispatcher, report back
- "Read these 10 GitHub issues and tell me which ones are still relevant" → 1 dispatcher with all 10 URLs
- "Survey 5 competing libraries for X and recommend one" → N dispatchers (one per library) → parent synthesizes
- "Read this PDF and extract the 5 key claims" → 1 dispatcher
- Anything where the *reading* is heavy but the *answer* is short

## When NOT to dispatch

- You need to write or edit files → use direct tools or `/swarm`
- The question is short and you can answer from memory → just answer
- The answer requires conversation with the user → keep it in the parent session
- You need cross-worker coordination → use `/swarm` (worktrees) instead

---

## How you operate

### 1. Frame the task

Rephrase the user's request as a self-contained prompt for the worker. The worker has no conversation history — give it everything: context, files to read, URLs to fetch, the exact question to answer, and the output format.

A good worker prompt has four parts:
1. **Context** — what the parent session is doing and why this matters
2. **Inputs** — files/URLs/topics to investigate (be specific; absolute paths)
3. **Question** — the single thing you need answered
4. **Output format** — exact structure for the response (e.g., "Return a markdown table with columns: lib, license, last_release, verdict")

### 2. Choose N

- Default `--n 1`. One worker is the right answer most of the time.
- Use `--n > 1` only when the task naturally splits (5 libraries, 10 docs) and each worker can be told a *different* subset.
- If `--n > 1`, you need a per-worker prompt — do NOT send the same prompt to 5 workers and hope for diversity.

### 3. Spawn

For each worker:

```bash
claude -p "<worker_prompt>" \
  --permission-mode plan \
  --allowedTools Read,Glob,Grep,WebFetch,WebSearch \
  --model "${MODEL:-claude-sonnet-4-6}" \
  --max-tokens "${MAX_TOKENS:-4000}" \
  > outputs/dispatch/<ts>/worker-<n>.md 2>&1
```

Run in parallel if N > 1 via background jobs + `wait`. Cap at N=10; if user asks for more, refuse and explain that 10 fresh contexts is the point where the synthesis cost exceeds the parallelism gain.

`--permission-mode plan` makes this read-only. Workers cannot edit files, run mutating shell commands, or call agents themselves. This is the load-bearing safety property.

### 4. Synthesize

When all workers finish:
- Read each `worker-<n>.md`
- Produce a single combined report for the parent session
- Cite which worker said what when answers diverge
- Resolve contradictions by re-reading source material yourself if needed (do NOT spawn more workers to resolve — that's recursion)

### 5. Report

Show the user:
- The synthesized answer (the actual content they wanted)
- A footer: `dispatched N workers, total ~X tokens, see outputs/dispatch/<ts>/ for raw reports`

The user almost never needs the raw worker output. Keep it on disk for audit; don't paste it into the session.

---

## Hard rails

- **Read-only.** Workers must use `--permission-mode plan`. No exceptions. If the task needs writes, you're using the wrong skill — switch to `/swarm` or direct tools.
- **Cap N at 10.** Beyond that the synthesis step becomes the bottleneck.
- **Cap total wall time at 10 minutes per worker.** Use `timeout` (or the bash 3.2 fallback chain from `/swarm`'s dispatch.sh).
- **Cost awareness.** Print an estimate before spawning: `~$0.02–0.10 per worker on Sonnet`. If N×est > $2, ask the user to confirm.
- **Never let a worker spawn another worker.** Strip `Agent` and `Bash` from `--allowedTools` to enforce this. If a worker is told to use `Agent`, it should refuse.

---

## Output location

All dispatch runs land in `outputs/dispatch/<UTC-timestamp>/`:
- `prompt-<n>.md` — the exact prompt sent to worker N
- `worker-<n>.md` — the worker's report
- `synthesis.md` — your combined output
- `summary.json` — `{ ts, n, model, total_tokens_estimate, wall_seconds }`

---

## Handoff

After synthesizing, present the answer plainly to the user. If the answer suggests a next action (e.g., "library X looks best — install it?"), prompt for it. Do not chain into other skills automatically — dispatch is a one-shot research tool, not a pipeline stage.
