# tanker — project instructions

This file is auto-loaded by Claude Code at the start of every session in this repo.

## What this project is

tanker — a Claude Code skill + agent framework. Skills, agents, always-on rules, a three-layer memory system, an autopilot orchestrator (`/cto`), and local semantic retrieval over a personal knowledge corpus.

## Conventions (apply always)

- Skills at `.claude/skills/[name]/SKILL.md` with YAML frontmatter (name, description, triggers, args)
- Always-on rules in `.claude/rules/` — builder-ethos, code-standards, static-site-standards, claude-executes
- Agents in `.claude/agents/[name].md`
- All skill output goes to `outputs/[project-name]/` (gitignored — local-only)
- Every skill ends with a handoff line pointing to the next skill in the chain
- Stage files explicitly by name when committing — never `git add .` (prevents accidental .env / credential leaks)
- After modifying any skill / rule / agent, commit on a feature branch and open a PR (branch protection blocks direct push to main)

## Project memory split

Two memory files live next to this one:

- **`.claude/brain.md`** — tracked. Framework-level conventions, decisions, pitfalls, preferences. Safe to be public.
- **`.claude/brain.private.md`** — gitignored. Project-specific context, work-in-progress, anything sensitive. Read in sessions but never committed.

Both are auto-loaded by the global session-memory rule in `~/.claude/CLAUDE.md`. Anything project-specific or sensitive belongs in `brain.private.md`, never in `brain.md` or this file.

## What does NOT belong in tracked files

This repo is public. The following must never appear in tracked files (CLAUDE.md, brain.md, skill prompts, examples, outputs):

- Internal company strategy, unreleased product names, internal pricing, internal team member names, customer names, GMV figures
- Personally identifying information beyond the owner's already-public profile
- Hardcoded credentials, API keys, OAuth tokens, webhook URLs tied to private accounts
- Notion page IDs / Slack channel IDs / internal URLs from the day job
- Absolute filesystem paths revealing the owner's machine layout (use `~/` form)

If you (Claude) are about to add any of the above to a tracked file — stop. Put it in `.claude/brain.private.md` instead, or save it as an in-memory note and ask the owner where it should live.
