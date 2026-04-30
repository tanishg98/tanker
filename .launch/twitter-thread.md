# X / Twitter launch thread

## Thread (10 tweets)

**1/ (hook)**

```
i built a Claude Code framework that ships deployed products from a one-line brief.

`/cto "todo app with auth and a kanban view"`
→ live URL in ~3 hours
→ ~30 min of my attention total

Tanker. MIT. Repo + demo GIF below ↓
```

(Attach: 30-second demo GIF.)

**2/ (the move)**

```
the trick isn't autopilot. autopilot ships slop.

the trick is two human gates pre-qualified by review agents:
1. PRD review (after prd-reviewer PASSes)
2. MVP review (after mvp-reviewer PASSes)

you only see what's worth seeing.
```

**3/ (provisioning)**

```
most "build a product" tools end with code on disk.

tanker provisions:
• github repo + branch protection
• supabase project + RLS
• vercel project + env vars
• railway service + healthcheck

via real APIs, from a vault at ~/.claude/vault/credentials.json (0600).
```

**4/ (resumability)**

```
state.json is checkpointed every phase.
messages.jsonl is the typed audit trail (cause_by, sent_from, send_to — borrowed from MetaGPT).

`/cto --resume <slug>` picks up exactly where you left off.
laptop dies mid-build? no problem.
```

**5/ (cost)**

```
cost ceiling is built in.

`/cto "..." --max-cost-usd 20`
default $10. warns at 70%, halts gracefully at 100%.

`/cto --audit <slug>` prints per-phase token + cost table.
no surprise bills.
```

**6/ (retrieval)**

```
local semantic retrieval over your stuff:

• brain-index → your Obsidian vault
• refs-index → curated GitHub repos you find inspiring

/cto Phase 1 queries both before doing anything else. all embeddings local. nothing leaves the machine.
```

**7/ (comparisons)**

```
honest comparisons in the docs:

• MetaGPT — they have the paper, we have the deployed URL
• AutoGen — different scope, conversation framework
• CrewAI — generic vs opinionated
• Aider — line-level pair programming, complementary
• gstack — same primitives, different opinions

→ tanker.dev/comparisons
```

**8/ (what i borrowed)**

```
honest credit:

borrowed from MetaGPT:
1. typed Message envelope schema
2. SOP triplet prompt pattern (Constraints + Reference + Output Format)
3. bounded review-retry loop
4. DataInterpreter pattern (Tanker's /analyst)

put `--max-cost-usd` on top.
```

**9/ (call)**

```
i build for indian D2C operators. tanker carries that taste:

• "no AI slop" ban list (no purple gradients, no centered everything, no generic hero copy)
• light-mode-only for SMB tools
• mobile-first responsive
• Anthropic editorial CSS for stakeholder docs

opinionated end-to-end.
```

**10/ (CTA)**

```
github: https://github.com/tanishg98/tanker
docs: https://tanker.dev
discord: <link>

MIT. one-line install. /cto away.

if you ship something with tanker, post in #show-your-build. that's the fastest way to feedback.

(thanks @AnthropicAI for Claude Code.)
```

## Tag list (pin this for the day)

Tag in replies, not in the main thread (HN-style soft promotion):
- @AnthropicAI
- @claudeai
- @swyx
- @nutlope
- @theo
- @garrytan (gstack precedent)
- @paulgauthier (aider)
- @msfteng (autogen)

## Don't

- Don't write em dashes — they're Tanish's stylistic flag, but the launch thread wants line breaks instead. Per [feedback memory](no-em-dashes).
- Don't tag everyone in tweet 1. Tag in replies once the thread has organic engagement.
- Don't pin the thread above an unrelated tweet. Pin Tanker thread for 7 days, then unpin.

## Engagement playbook

- Reply within 30 min to every quote-tweet.
- Don't engage with snark. One sentence reply if substantive, ignore otherwise.
- If a known builder retweets, reply-thank within 1 hour.
