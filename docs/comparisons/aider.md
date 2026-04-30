# Tanker vs Aider

[Aider](https://github.com/Aider-AI/aider) is an in-terminal AI pair programmer. It edits code in your repo with git-aware diffs.

## TL;DR

- **Aider is a pair programmer.** Tanker is a product-build pipeline.
- **Aider edits files.** Tanker also provisions, deploys, and monitors.

These tools are complementary, not competitive. You can use Aider for line-level pair programming and Tanker for new-product autopilot.

## Side-by-side

| | Aider | Tanker |
|---|---|---|
| **Primary use case** | Edit code in an existing repo | Build a new product from a brief |
| **Interaction model** | Conversational, edit-by-edit | Phased pipeline with human gates |
| **Git integration** | Native (commits, diffs, revert) | Via `/ship` skill |
| **PRD / architect / plan** | No | Yes — exhaustive PRD + architecture + plan as artifacts |
| **Provisioning** | No | Yes — gh + supabase + vercel + railway |
| **Quality gates** | Linting/tests if configured | pre-merge + autoresearch + prd-reviewer + mvp-reviewer |
| **Multi-LLM** | Yes | Claude Code-native |
| **Cost tracking** | Token meter in TUI | `--max-cost-usd` cap + per-Message audit |

## What Tanker borrows from Aider

- **Git-as-source-of-truth philosophy.** Aider's "every edit is a commit" model informs Tanker's `/ship` skill discipline.

## What's different

- **Aider is line-level.** Tanker is product-level.
- **Aider has no PRD or architect phase.** It assumes you already know what to build.
- **Aider doesn't deploy.** Tanker does.

## When to use which

**Aider if** you have a clear coding task in an existing repo and want fast in-terminal edits with git-aware diffs.

**Tanker if** you're starting a new product, or if you want to add a substantial feature with proper PRD → architect → plan → build → deploy discipline.

## Use both

Aider for daily pair-programming on existing Tanker-built repos. Tanker (`/cto`) for new builds. Tanker's `/explore` + `/createplan` + `/execute` flow can replace Aider for feature work, but Aider's TUI pace is hard to beat for tight inner-loop edits.
