# What only you can do

> **Status update (post-merge):** PR #3 is merged to `main`. Real Persona Studio screenshots are the README hero. Most of Phase 0 below is now ✅ done.
>
> **Tomorrow morning's plan** lives in [`.launch/morning-schedule.md`](./.launch/morning-schedule.md) — that's the active file. This checklist is the wider rollout reference.

Everything in this checklist requires **your account access, your wallet, your face, your brand judgment.** I (Claude) have done everything else — code, schemas, docs, launch copy. This is your runway.

The list is ordered. Don't skip steps; the launch fails on omissions, not bad copy.

---

## Phase 0 — Sanity check before launch (30 minutes)

Bar: every item below is true *before* you announce anything.

- [ ] **Run `/cto` end-to-end on a small brief.** Watch it work. Capture rough timing. If it breaks, fix and re-test before launch.
- [ ] **Record the demo GIF.** 30-second screen recording of `/cto "snake game"` (or similar trivial brief) producing a deployed URL. Tools: [Kap](https://getkap.co/) on Mac, or QuickTime + GIPHY Capture. Save as `assets/demo.gif`. Replace the placeholder in README.md line 13.
- [ ] **Verify `install.sh` runs clean on a fresh checkout.** `cd /tmp && git clone <fork> && cd <fork> && bash install.sh`. If it errors, fix.
- [ ] **Open the docs site locally.** `pip install mkdocs-material && mkdocs serve`. Walk every page. Fix broken internal links.
- [ ] **Read every comparison page.** I wrote them honestly but I might have a fact wrong about MetaGPT/AutoGen/CrewAI. You're the operator who has to defend these in HN comments — make sure you stand behind every claim.
- [ ] **Decide on naming on the public-facing brand.** README says "Tanker". Lowercase brand "tanker" appears in some places. Pick one and grep-replace.

---

## Phase 1 — Hosted assets (1–2 hours)

- [ ] **Buy `tanker.dev`.** Namecheap or Cloudflare Registrar. ~$15/year.
- [ ] **Set up GitHub Pages or Cloudflare Pages on the docs site.** The `.github/workflows/docs.yml` workflow is already wired — enable Pages in repo settings, workflow will deploy on next push to main.
- [ ] **Point `tanker.dev` at the Pages deployment.** CNAME or A record per Pages instructions.
- [ ] **(Optional but high-impact) Set up `tanker.dev` landing page.** A single-file HTML hero. The docs site lives at `/docs/`, the landing at `/`. If skipping for v1, make `tanker.dev` redirect to docs.
- [ ] **Discord server.** Three channels minimum: `#show-your-build`, `#help`, `#contribute`. Pin the examples directory link in `#show-your-build`. Create a vanity URL.
- [ ] **GitHub repo settings:**
  - [ ] Add description: "A Claude Code framework that ships deployed products from a one-line brief."
  - [ ] Topics: `claude-code`, `ai-agents`, `multi-agent`, `autopilot`, `mcp`, `metagpt`, `autogen`.
  - [ ] Pin `tanker.dev` in the website field.
  - [ ] Enable Issues + Discussions.
  - [ ] Set up `CODE_OF_CONDUCT.md` (use Contributor Covenant).
  - [ ] Set up `CONTRIBUTING.md` (steal from any well-run OSS repo).

---

## Phase 2 — Pre-launch content (2–3 hours)

- [ ] **Fill in real `examples/saas-mvp/transcript.md`** with one real `/cto` run. The placeholder won't fly. Pick a small product (todo app, expense tracker, simple CRM) and run `/cto` against it. Capture the messages.jsonl, redact secrets, paste into transcript.md.
- [ ] **Optionally fill in 1–2 more example transcripts.** Static-site and bug-fix are the cheapest. The other three can stay as placeholders for v1; PR fillers later.
- [ ] **Take 3 screenshots** for the docs / Twitter / LinkedIn:
  - [ ] `/cto` running, mid-pipeline, terminal screen
  - [ ] An `outputs/<slug>/prd/index.html` wireframe page
  - [ ] A `messages.jsonl` snippet (jq-pretty-printed)
- [ ] **Pre-write the dev.to / Hashnode launch post.** I have the draft at `.launch/devto-blog-post.md`. Personalize. Post on **Wednesday** (one day after Show HN), not the same day — different traffic source.

---

## Phase 3 — Launch day (Tuesday — full day at desk)

Order of operations. Don't reorder.

| Time (PT) | Action | Source file |
|---|---|---|
| 12:01 AM | Submit to Product Hunt | `.launch/producthunt.md` |
| 8:55 AM | Be at desk, refresh ready | — |
| 9:00 AM | Submit Show HN | `.launch/show-hn.md` |
| 9:01 AM | Post first comment on Show HN | `.launch/show-hn.md` (the maker comment) |
| 12:00 PM | X/Twitter thread | `.launch/twitter-thread.md` |
| 12:05 PM | LinkedIn post | `.launch/linkedin.md` |
| 1:00 PM | r/LocalLLaMA post | `.launch/reddit-localllama.md` |
| 2:00 PM | r/ClaudeAI post | `.launch/reddit-claudeai.md` |
| 3:00 PM | r/ChatGPTCoding post | `.launch/reddit-chatgptcoding.md` |
| 4:00 PM | Cold emails to 4 named recipients | `.launch/email-template.md` |

Stay at desk until 9 PM PT. Reply within 30 min to every substantive comment everywhere.

---

## Phase 4 — Day 2 (Wednesday)

- [ ] **Publish dev.to / Hashnode launch post.** `.launch/devto-blog-post.md`.
- [ ] **DM 5 specific builders** in your network with personalized notes.
- [ ] **Submit PR to awesome-claude:** https://github.com/anthropics/awesome-claude (or whatever the canonical "awesome-claude" list is at the time). Same for `awesome-ai-agents`, `awesome-llm-apps`.
- [ ] **Reply to every comment from yesterday** that you missed. The 24-hour-late reply still earns goodwill.

---

## Phase 5 — Sustained (weeks 2–8)

- [ ] **Friday changelog post.** Every Friday on Twitter + docs site. "What shipped in Tanker this week." Even small fixes count.
- [ ] **One "build with Tanker" video per week.** 5-min screen recording of `/cto` building something real. YouTube + LinkedIn + X.
- [ ] **One worked example PR per week.** Add to `examples/` directory. Helps SEO + adoption.
- [ ] **Discord office hours** weekly, 1 hour. Pin the time in #help.
- [ ] **First contributor merged within 2 weeks.** Find a small bug or doc gap, walk a stranger through fixing it. The first non-Tanish PR is the unlock for the second.

---

## Phase 6 — Defend honestly

If MetaGPT / AutoGen / CrewAI / gstack maintainers engage:

- [ ] **Be respectful.** Their work made Tanker possible. Credit them in replies.
- [ ] **Don't claim Tanker is "better."** Claim it's "different and opinionated." This is true and defensible.
- [ ] **Fix anything they correctly point out.** If a comparison claim is wrong, edit the docs and apologize publicly.

---

## What I (Claude) cannot do — but am ready to help with

- **Implement Phase B steals (#7 per-agent memory slice, #8 pub-sub Environment).** Ask me to do this in a separate PR after launch. They're isolated changes.
- **Write the per-skill mkdocs pages.** Right now they're stubs pointing at SKILL.md. If you want full mkdocs pages with examples per skill, ask.
- **Fill in example transcripts.** I can run `/cto` for you in a fresh project but I can't capture the GIF — the actual recording requires your screen.
- **Reply to HN comments.** You have to. The voice has to be yours, and HN smells AI-generated comments.

---

## What you should NOT do

- ❌ Don't launch without the GIF.
- ❌ Don't launch on a Friday or weekend.
- ❌ Don't post on a sub you're not a real member of.
- ❌ Don't ask anyone to upvote.
- ❌ Don't reply to snark.
- ❌ Don't stack multiple launches in the same week.
- ❌ Don't promise features that aren't built. The README only lists what's there.

---

Status of pre-launch deliverables (already shipped on `main`):

- ✅ Memory schema fixed (`project_tanker.md` + `project_obsidian_brain.md`, old confused file deleted)
- ✅ Typed Message envelope schema (`.claude/skills/cto/message-schema.md` + `.claude/schemas/message.schema.json`)
- ✅ SOP triplet (Constraints / Reference / Output Format) on `/prd`, `/architect`, `/createplan`, `pre-merge`
- ✅ `--max-cost-usd` budget cap in `/cto` SKILL.md
- ✅ Bounded retry loop (max 2 retries) in build phase
- ✅ JSON sidecar schemas for top 5 outputs (`.claude/schemas/{prd,architecture,plan,review,message}.schema.json`)
- ✅ `/analyst` skill (Python sandbox + ReAct loop) at `.claude/skills/analyst/SKILL.md`
- ✅ Per-agent memory slice (ChromaDB metadata filters: `--domain frontend|backend|data|infra|...`)
- ✅ Pub-sub Environment for /cto (subscription registry in agent frontmatter)
- ✅ `/cto --rerun-from <msg_id>` selective replay
- ✅ Multi-model `tanker.yaml` (Opus for hard reasoning, Sonnet for build, Haiku for cheap loops)
- ✅ One-line installer: `install.sh`
- ✅ Examples directory: `examples/{saas-mvp,static-site,browser-extension,bug-fix,data-analysis}/{brief,transcript}.md`
- ✅ mkdocs site: `mkdocs.yml` + `docs/` tree + GitHub Pages workflow
- ✅ Comparison pages: `docs/comparisons/{metagpt,autogen,crewai,aider,gstack}.md`
- ✅ README rewrite + real Persona Studio hero GIF
- ✅ Launch copy package: `.launch/{show-hn,twitter-thread,reddit-*,producthunt,linkedin,devto-blog-post,email-template,morning-schedule}.md`

**On the v1.1 roadmap (after launch):**

- Hosted `tanker.dev` with one-click `/cto`
- Multi-LLM provider support (currently Claude Code-native)
- `/cto --rerun-from <msg_id>` runtime wiring (spec exists; orchestrator pass not yet implemented)

The launch doesn't depend on these.
