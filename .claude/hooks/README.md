# Tanker Hooks

Claude Code hooks wired via `.claude/settings.json`. These execute automatically on harness events — Claude does not control them.

## stop-auto-review.sh

Fires on session-end (Stop event). When the working tree has > 5 changed lines of real code, spawns a read-only `review` agent in a fresh `claude -p` context and writes a verdict (PASS / CONDITIONAL / FAIL) to `outputs/auto-review/<ts>.md`.

**Safety properties:**
- Read-only — agent runs in `plan` permission mode, cannot edit files
- Capped at 3 auto-iterations per session (counter resets on a clean diff)
- 5-minute watchdog per invocation
- Skips trivial diffs and noise files (`.claude/git-state.md`, `agent-tasks/`)

**Wire it up** by adding to `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "./.claude/hooks/stop-auto-review.sh" }
        ]
      }
    ]
  }
}
```

**Disable for one session:** `TANKER_AUTOREVIEW_MAX=0 claude`
**Raise iteration cap:** `TANKER_AUTOREVIEW_MAX=10 claude`

**Loop intent:** the article calls for "if review fails, auto-spawn /execute to fix, loop until green." This first version does the review only — the fix loop is intentionally not auto-wired because auto-edits triggered by a Stop hook would surprise the user mid-session. Promote to a fix loop manually after a week of read-only confidence.
