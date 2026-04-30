# Tomorrow morning schedule

> Copy-paste-ready. Designed around the new angle: **Tanker built a real product — Persona Studio.** The proof IS the product.

## Timing (your local time, IST)

- **8:30 AM IST** — X post
- **8:35 AM IST** — LinkedIn post
- **9:00 AM IST onwards** — Reddit comments (organic, not announcements)

8:30 AM IST = end of US Tuesday evening + start of Europe morning. Catches both timezones in their feed-checking windows.

---

## X / Twitter — single post (recommended, not thread)

Single posts get more engagement than threads for "I built X" announcements. Attach `assets/demo.gif` as the media.

```
i built a Claude Code framework called tanker. 

then i used tanker to build this:
https://persona-studio-lime.vercel.app

india-first AI influencer studio. one /cto brief → deployed product.

framework MIT, repo + comparisons in replies ↓
```

**Reply 1 (post 30 sec after):**
```
github: https://github.com/tanishg98/tanker

opinionated rails: two human gates pre-qualified by review agents, real provisioning (gh + supabase + vercel + railway), cost ceiling --max-cost-usd, typed message envelope per artifact, /analyst skill for data work
```

**Reply 2 (post 60 sec after):**
```
honest comparisons in the docs vs MetaGPT, AutoGen, CrewAI, Aider, gstack:
https://github.com/tanishg98/tanker/tree/main/docs/comparisons

(tldr: tanker ends in a deployed URL. they end in code on disk.)
```

**Tag in replies, not main post:**
@AnthropicAI @claudeai @swyx @nutlope @theo

### Why single post + replies vs full thread

- Engagement on follow-up replies is much higher than on tweet 4/10 of a thread
- The image renders bigger
- Easier to share
- Repliers add their own thread context

### Don't

- ❌ Don't use em dashes (per voice rule)
- ❌ Don't tag everyone in main post
- ❌ Don't say "really excited to announce" — sounds like a launch press release
- ❌ Don't end with a CTA like "RT please"

---

## LinkedIn post

Keep it medium-long. LinkedIn rewards "I learned something" energy over "I built a thing."

```
Six months ago I started using Claude Code as a daily driver.

Every session started blank. Same conventions to re-explain. Same handoffs to wire. Same quality bar to enforce. I lost hours per week to reset friction.

So I built tanker — a Claude Code framework with 34 slash skills, 9 agents, 3 always-on rules, and a /cto autopilot that turns a one-line brief into a deployed product.

The test: I used tanker to build Persona Studio (https://persona-studio-lime.vercel.app), an India-first AI influencer creator. From brief to live URL in one weekend, two human review gates, ~30 minutes of my actual attention.

Three opinionated choices that came from real failures:

1. Two human gates instead of full autonomy. I tried fully-autonomous for a week. It shipped slop. The gates are at the points where human judgment compounds (PRD review, MVP review). Each gate is pre-qualified by a review agent so I only see what's worth reviewing.

2. Real infrastructure provisioning. Most "AI builds your product" tools end with code on disk. Tanker provisions GitHub + Supabase + Vercel + Railway via APIs from a vault at 0600 perms.

3. Cost ceiling built in. --max-cost-usd default $10, halts gracefully at 100%, resumes with a higher cap. No surprise bills from runaway agent loops.

Borrowed honestly from MetaGPT (typed Message envelope, SOP triplet prompt pattern, bounded retry loop). Disagreed with them in three places (full autonomy, code-as-output, no cost ceiling).

Open source, MIT. Honest comparisons in the docs vs MetaGPT, AutoGen, CrewAI, Aider, gstack.

Repo: https://github.com/tanishg98/tanker
Live demo of what it built: https://persona-studio-lime.vercel.app

If you build with Claude Code daily, would love your read. Most-useful feedback I'm hoping for: would you trust two-pre-qualified gates over fully-autonomous? Or want more / fewer gates?

#AI #ClaudeCode #OpenSource #ProductManagement
```

### LinkedIn tactical notes

- Native upload `assets/demo.gif` (don't just link to GitHub)
- Don't tag your CEO or company. Personal post.
- Reply within 2 hours to every comment for the first 4 hours

---

## Reddit — DON'T post a launch announcement (per your direction)

Instead, drop **organic helpful comments** on existing threads. These convert better than launch posts because Reddit hates self-promotion.

### Where to look

Search these subs daily for the next 7 days:

| Sub | Search terms |
|---|---|
| r/ClaudeAI | "claude code", "autopilot", "framework", "agent", "skill" |
| r/LocalLLaMA | "agent framework", "metagpt", "autogen", "crewai" |
| r/ChatGPTCoding | "ai coding", "framework", "ship product" |
| r/MachineLearning | "agent SOP", "multi-agent" (be careful, academic crowd) |

### Comment template (when relevant — don't spam)

When someone asks "what's the best multi-agent framework for X" or "how do I keep Claude Code consistent across sessions" — drop this:

```
i had the same problem and ended up building tanker (open source, MIT) to handle it. it's a Claude Code framework with 34 skills, 9 agents, two pre-qualified human review gates. one /cto command turns a brief into a deployed product (real example: persona-studio-lime.vercel.app).

if you've used MetaGPT, the architecture is similar (borrowed the typed Message envelope + SOP prompt pattern). main differences: ends in deployed URL not code, two human gates pre-qualified by review agents, cost ceiling --max-cost-usd default $10.

repo + honest comparisons: https://github.com/tanishg98/tanker

happy to answer specific questions
```

### Rules for Reddit

- Comment ≠ post. You're not announcing, you're helping. The link is incidental.
- Reply only to threads where Tanker is genuinely on-topic. Spamming gets you banned.
- 1 comment per sub per week max. Quality > volume.
- Always answer the OP's actual question first. Then mention Tanker IF relevant.

---

## What ELSE to do (no Product Hunt, no influencer DMs)

Per your "GitHub-only" direction. These are all low-effort, high-leverage:

### Today (10 min total)

- [ ] **GitHub repo description** — paste this in repo settings:
  ```
  A Claude Code framework that ships deployed products from a one-line brief. Two human gates, real provisioning (gh + supabase + vercel + railway), cost ceiling, /analyst skill, MIT.
  ```

- [ ] **GitHub topics** (settings → topics) — add all of these:
  ```
  claude-code, ai-agents, multi-agent, autopilot, metagpt, autogen, crewai, aider, llm, agent-framework, ai-coding-assistant, vercel, supabase
  ```

- [ ] **Add a "social preview" image** to the repo — Settings → Social preview → upload `assets/hero.png` (the Persona Studio landing screenshot). This is what shows when the link is shared anywhere.

### This week (15 min total)

- [ ] **Submit awesome-list PRs:**
  - https://github.com/hesreallyhim/awesome-claude-code (search for the canonical one)
  - https://github.com/e2b-dev/awesome-ai-agents
  - https://github.com/steven2358/awesome-llm-apps

  Format the PR with one line: `- [tanker](https://github.com/tanishg98/tanker) - Claude Code framework that ships deployed products from a one-line brief.`

- [ ] **Submit to Hacker News' "Show HN"** — even though you skipped Product Hunt, Show HN is GitHub-traffic-driving by design. Tuesday 9 AM PT. Copy at `.launch/show-hn.md`.

- [ ] **Cross-post LinkedIn → personal blog or dev.to** — 24 hours after the LinkedIn post, drop the same content on dev.to with `#showdev` tag. Long-tail SEO + Google ranks dev.to.

### Sustained (5 min/week)

- [ ] **Friday weekly tweet** — "what shipped in tanker this week." Even small fixes count. Builds compounding follower count, signals active development.

- [ ] **Reply to every GitHub issue + PR within 24 hours.** Active maintenance is the #1 signal that converts a star into a daily user.

- [ ] **Add 1 new example transcript per week** to `examples/`. Each one is a permanent SEO + credibility artifact.

### Skip these (per your direction or low ROI)

- ❌ Product Hunt
- ❌ Discord (defer until 500+ stars)
- ❌ Cold emails to influencers (low conversion)
- ❌ Paid ads (wrong audience)
- ❌ YouTube videos (high effort, do later if you have momentum)

---

## Expected math

If you do exactly what's in this file (X + LinkedIn tomorrow, awesome lists this week, Show HN Tuesday):

- **Tomorrow:** X gets ~50-200 likes, ~5-30 stars. LinkedIn gets ~30-150 reactions, ~5-15 stars. Cumulative: ~10-50 stars.
- **Week 1** (with awesome-list merges + Show HN Tuesday): 500-1500 stars.
- **Month 1** (sustained Friday cadence + organic): 1000-2500 stars.

This is realistic if Persona Studio actually works (which it does — it's live).

---

## What to do NOW (before bed tonight)

So tomorrow morning is just hitting "post":

- [ ] **Schedule the X post** — use Twitter's native scheduler or Typefully/Buffer. Time it for 8:30 AM IST tomorrow.
- [ ] **Schedule the LinkedIn post** — LinkedIn's native scheduler is fine. 8:35 AM IST.
- [ ] **Test that both have the GIF attached** — preview before scheduling.
- [ ] **Set a calendar reminder** for tomorrow 8:30 AM to be at desk for replies.
- [ ] **Open `assets/hero.png`** — confirm it's the right hero image. Upload to GitHub repo settings → Social preview.

That's it. Total tonight: 10 minutes.

Sleep. Tomorrow morning you wake up, the posts go live, you reply to comments. By Tuesday Show HN, you have early signal for refinement.
