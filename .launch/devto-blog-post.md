# Launch blog post — dev.to / Hashnode / personal site

## Title

```
I built a Claude Code framework that ships deployed products from a brief. Here's what I borrowed from MetaGPT, and where I disagreed with them.
```

## Tags

`#ai`, `#opensource`, `#productivity`, `#showdev`, `#claude`

## Body

````markdown
For the past few months, I've been building Tanker — a Claude Code framework that turns a one-line product brief into a deployed product, with two human review gates and real infrastructure provisioning. It's open source, MIT, and lives at [github.com/tanishg98/tanker](https://github.com/tanishg98/tanker).

This post is about three things:
1. Why I built it (and why "fully autonomous code generation" isn't the right primitive).
2. What I borrowed from MetaGPT (honestly).
3. Where I disagreed with them, and how those disagreements shaped Tanker.

If you've used MetaGPT, AutoGen, CrewAI, or Aider, the comparison should be useful. If you haven't, the architectural moves are interesting on their own.

## The problem

I work out of the CEO's Office at Shiprocket (India's largest D2C logistics platform), building everything with AI. I ship side projects on weekends and wedge AI features into the day job. Claude Code became my daily driver about six months ago — it's the best in-terminal AI coding tool I've used.

But every session starts blank. Same conventions to re-explain. Same handoffs to re-wire. Same quality bar to re-enforce. After ~50 sessions of this, I built Tanker: a `.claude/` folder you drop into any project. 34 slash skills, 9 specialist agents, 3 always-on rules.

The headline command is `/cto "<one-line brief>"`. It runs:

```
intake → context (parallel: brain-index + refs-index)
  → /grill → /benchmark? → /prd → prd-reviewer → 🛑 GATE 1
  → /architect → /createplan → /advisor (cross-model peer review)
  → PROVISION (parallel: gh + supabase + vercel + railway via real APIs)
  → BUILD (parallel: frontend + backend + data + content engineers)
  → /pre-merge + /autoresearch-review per PR (bounded retry)
  → mvp-reviewer → 🛑 GATE 2
  → /deploy → /monitor → final report
```

End state: a live URL, a repo with branch protection, monitoring wired. Total owner attention: ~30 minutes (two reviews × ~15 min each).

## What I borrowed from MetaGPT

[MetaGPT](https://github.com/FoundationAgents/MetaGPT) (40k+ stars, ICLR 2024 paper) is the cleanest multi-agent code-generation framework I've read. Four architectural moves are directly visible in Tanker.

### 1. Typed Message envelope

MetaGPT's `metagpt/schema.py` wraps every artifact in a `Message` with `cause_by`, `sent_from`, `send_to`, `instruct_content`. This is what makes a multi-agent run replayable, auditable, and selectively re-runnable.

I had Tanker writing free-form `state.json` blobs. Provenance was lost. Review agents had to re-parse markdown to recover what skill produced what. After reading MetaGPT's schema, I added a typed Message envelope to Tanker's `outputs/<slug>/messages.jsonl`. One line per artifact:

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
  "in_reply_to": "msg_01HW...",
  "tokens_in": 8421,
  "tokens_out": 12044,
  "cost_usd": 0.193,
  "status": "ok"
}
```

Now `/cto --audit <slug>` produces a per-phase token + cost breakdown. The cost ceiling is enforced against this. Replay queries are one-liners with `jq`.

### 2. SOP triplet prompt pattern

Every MetaGPT action prompt has three rigid sections: Constraints (non-negotiable rules), Reference (a worked example), Output Format (validated schema). I'd been writing skill prompts as conversational walls of text. After refactoring `/prd`, `/architect`, `/createplan`, and `pre-merge` to the SOP triplet, output consistency went up noticeably.

```
## SOP — Constraints / Reference / Output Format

**Constraints (non-negotiable):**
- Every section in the skeleton must be present, in order.
- Every screen must have at least 3 enumerated states.
- "TBD" or "[…]" or "etc." are blocking — write the content or remove the section.

**Reference example (lift the structure verbatim):**
- See MetaGPT's `metagpt/actions/write_prd_an.py` for the few-shot pattern.

**Output Format:**
1. `outputs/<slug>/prd/prd.md` — narrative
2. `outputs/<slug>/prd/index.html` — HTML wireframes
3. `outputs/<slug>/prd/prd.json` — machine-readable, validated against `.claude/schemas/prd.schema.json`
```

### 3. Bounded review-retry loop

MetaGPT's `WriteCodeReview` runs review → fix → review up to `n` iterations, capped to avoid infinite loops. I added the same to Tanker's Phase 5 build:

```python
attempt = 0
while attempt < 3:  # original + 2 retries
    pre_merge = run_agent("pre-merge", pr)
    if pre_merge.verdict == "PASS": merge(); break
    if pre_merge.verdict == "PASS_WITH_FIXES" and not has_ASK_findings:
        dispatch_subagent_with_fixes()
    else:
        dispatch_subagent_with_failure_report()
    attempt += 1

if attempt == 3: escalate_to_human()
```

Catches obvious slop before the human gate. Beyond 2 retries, the failure is structural — surface to human, don't burn tokens.

### 4. DataInterpreter → /analyst

MetaGPT's `DataInterpreter` is a ReAct loop that writes + executes Python. Tanker had nothing equivalent. I added `/analyst` — same Plan → Code → Execute → Reflect → Decide pattern, but Tanker's version sits inside the Claude Code Bash tool sandbox and writes a runnable `notebook.py` alongside the `report.md`. Every claim in the report has executed code behind it.

## Where I disagreed

### 1. Fully autonomous is the wrong default

MetaGPT runs end-to-end with no human gates. I tried that approach for a week with Tanker. It produced things that "ran" but were subtly wrong — wrong onboarding flow, missed edge cases in the data model, generic UI copy.

The fix wasn't more agent reviewers. It was two human gates at the highest-leverage decisions:
- **Gate 1: PRD review** — before code is written. If the PRD is wrong, the build is wrong.
- **Gate 2: MVP review** — before production deploy. If the MVP doesn't match the PRD, the deploy is wrong.

Both gates are pre-qualified by a review agent (`prd-reviewer`, `mvp-reviewer`). The owner only sees the gate after the agent returns PASS. So the human spends ~15 min per gate on the questions only a human can answer.

Total owner attention per `/cto` run: ~30 min for a deployed product. That's the right tradeoff for me.

### 2. Code generation isn't the product

MetaGPT ends with a repo on disk. Tanker provisions GitHub + Supabase + Vercel + Railway via real APIs, deploys, smoke-tests, and wires Sentry + analytics + uptime. The end state is a live URL with monitoring, not a folder of files.

This is a bigger gap than it sounds. The "last 20%" — provisioning, deploy, monitoring — is the work that breaks production. Real provisioning agents (`gh-provisioner`, `supabase-provisioner`, `vercel-provisioner`, `railway-provisioner`) are scoped, idempotent, and read from a vault at `~/.claude/vault/credentials.json` (0600).

### 3. Cost ceiling should be in the framework

MetaGPT has `SoftwareCompany.investment` but it's not enforced as a hard ceiling. I added `--max-cost-usd` (default $10) to Tanker. Tracked per-Message. Halts gracefully at 100%, warns at 70%. Resume with a higher cap if needed. Predictable spend matters for solo builders.

### 4. Generic frameworks ship slop

MetaGPT is taste-agnostic by design. Tanker is the opposite — `builder-ethos` rule encodes opinions: explicit "No AI Slop" ban list (no purple gradients, no centered everything, no generic hero copy), light-mode-only for SMB tools, mobile-first responsive, IntersectionObserver animations. The opinions cost generality but produce consistently better output.

### 5. Local retrieval over your stuff matters

`brain-index` indexes my Obsidian vault into local ChromaDB. `refs-index` does the same for curated GitHub repos I find inspiring. `/cto` Phase 1 retrieves from both before any other step. The orchestrator pulls from my accumulated knowledge, not generic GitHub search.

This is the one move I'm proudest of. Generic prior art is fine; my own prior art is better.

## What I'd build next

- **Multi-LLM** — borrowing MetaGPT's `config2.yaml` pattern. Today Tanker is Claude Code-native.
- **Hosted Tanker** at `tanker.dev` with a one-click `/cto` on a server. Free tier with rate limit.
- **`/cto --rerun-from <msg_id>`** — selective replay from any Message envelope. The schema is there; the orchestrator wiring isn't yet.
- **Pub-sub Environment** — agents subscribe to artifact types instead of a hardcoded DAG. Still thinking through whether this is worth the indirection for the orchestrator.

## Try it

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/tanishg98/tanker/main/install.sh)
/vault-add github vercel supabase anthropic
/cto "todo app with email auth and a kanban view"
```

Repo: https://github.com/tanishg98/tanker (MIT)
Docs: https://tanker.dev
Comparisons: https://tanker.dev/comparisons/

If you ship something with Tanker, post it. The fastest way to feedback that improves the framework.

---

*Tanish Girotra works out of the CEO's Office at Shiprocket, India — building everything with AI. He ships side-projects when he should be sleeping.*
````

## Don't

- Don't paste this verbatim on every site. Reword the intro per site.
- Don't link affiliate-style. The launch is open source; it's not a sales pitch.
- Don't use AI-slop subheadings ("Unlock the power of...", "Revolutionize your workflow"). The whole post is an argument against that aesthetic.
