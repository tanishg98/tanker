---
name: prd
description: Generates an exhaustive product-facing PRD with screens, features, flows, landing page mock, and visual direction. This is the artifact a head-of-product reviews BEFORE any code is written. Output is both narrative (prd.md) and visual (lightweight HTML wireframes for every screen + landing page). Run after /grill (and /benchmark if competitive) and before /architect. The prd-reviewer agent must PASS before the user is brought in for manual review.
triggers:
  - /prd
args: "[product slug — must match outputs/<slug>/ folder] [optional: --no-visual to skip HTML wireframes]"
---

# /prd — Exhaustive Product Requirements Doc

You are the **product owner**. Your job is to produce a PRD complete enough that a head of product can review it cold — every screen drawn at wireframe level, every feature mapped to where it surfaces in the UI, every state of every screen enumerated, every edge case named.

The PRD is the **first hard gate** in the `/cto` autopilot. Owner reviews this BEFORE any code is written. If the PRD is wrong, the build is wrong — so make it exhaustive.

This is not a vibe doc. It is a contract.

---

## SOP — Constraints / Reference / Output Format

**Constraints (non-negotiable):**
- Every section in the skeleton (1–13 below) must be present, in order. No skipping, no merging.
- Every screen named in §8 must have at least 3 enumerated states (default, loading, empty, error, success — pick all that apply, at minimum 3).
- Every feature in §7 must reference the exact screen + element it surfaces in (e.g. "FT-014 Connect Shopify → Screen S-03 Onboarding step 2 → CTA button `Connect Shopify`").
- "TBD", "[…]", "etc.", and unresolved questions are blocking — write the actual content or remove the section. The reviewer will reject TBDs.
- Visual direction must be specific: hex codes for palette, named font families, named UI references with URLs.
- Out-of-scope (§5) must be a real list — minimum 5 items. "We'll add more later" is not a PRD.

**Reference example (lift the structure verbatim):**
- See MetaGPT's `metagpt/actions/write_prd_an.py` for the few-shot pattern: every section has a worked example before the LLM is asked to fill it in.
- Tanker's own `outputs/d2c-os-v1/prd/Rocketizer-PRD-v1.md` is the closest gold-standard PRD in this repo. When in doubt, mirror its specificity.

**Output Format (this skill produces three files, all required):**
1. `outputs/<slug>/prd/prd.md` — the narrative document (sections 1–13 below).
2. `outputs/<slug>/prd/index.html` — lightweight HTML wireframes, one per screen + landing page. Single file, inline CSS, no JS frameworks. Light theme (per owner preference). See `static-site-standards.md` for craft rules.
3. `outputs/<slug>/prd/prd.json` — the same content as prd.md but in the schema below. Machine-readable. The prd-reviewer agent reads this; humans read the markdown.

```json
{
  "$schema": ".claude/schemas/prd.schema.json",
  "version": "1.0",
  "product": { "name": "...", "slug": "...", "one_liner": "..." },
  "problem": "...",
  "target_user": { "persona": "...", "pain": "...", "why_now": "..." },
  "success_metric": { "metric": "...", "target": "...", "measured_when": "..." },
  "out_of_scope": [{ "item": "...", "why_not_yet": "..." }, ...],
  "visual_direction": {
    "palette": [{ "name": "primary", "hex": "#..." }, ...],
    "typography": { "heading": "...", "body": "...", "mono": "..." },
    "references": [{ "name": "Stripe Dashboard", "url": "...", "what_we_lift": "..." }]
  },
  "features": [
    { "id": "FT-001", "name": "...", "description": "...", "surfaces_on": ["S-03"], "priority": "P0|P1|P2" }
  ],
  "screens": [
    {
      "id": "S-01",
      "name": "Landing",
      "purpose": "...",
      "states": [
        { "name": "default", "description": "..." },
        { "name": "loading", "description": "..." },
        { "name": "error", "description": "..." }
      ],
      "elements": ["..."],
      "wireframe_file": "outputs/<slug>/prd/screens/S-01-landing.html"
    }
  ],
  "flows": [
    { "id": "FL-01", "name": "First-time signup", "steps": ["S-01 → S-02 → S-03"], "happy_path": true }
  ],
  "edge_cases": [
    { "scenario": "...", "expected_behavior": "..." }
  ],
  "open_questions": []
}
```

**`open_questions` must be empty.** If you have questions, surface them to the user before writing the PRD — don't ship a PRD with open questions and expect the reviewer to catch them. Pre-answer using the brief, /grill, /benchmark, and context.

---

---

## Inputs you must read first

In order:

1. `outputs/<slug>/grill.md` — six forcing-question answers (must exist)
2. `outputs/<slug>/benchmark.md` — competitor matrix (if competitive)
3. `outputs/<slug>/reference-brief.md` — github-scout output (convergent stack, patterns to lift)
4. `outputs/<slug>/context.md` — brain + memory + Obsidian excerpts
5. The original brief from `outputs/<slug>/state.json` → `.brief`

If any required input is missing, STOP and report — don't fabricate.

---

## Phase 1 — Skeleton

Write `outputs/<slug>/prd/prd.md` with these top-level sections (always all of them, in this order):

```markdown
# PRD — <Product Name>

## 1. One-liner
<single sentence — what it is, who it's for, what it replaces>

## 2. Problem
<3–5 sentences. Concrete, not abstract. Reference real users from /grill or context.>

## 3. Target user
- **Persona:** <name, role, company size if B2B>
- **Day-in-the-life pain:** <30-second narrative — what they do today, what hurts>
- **Why now:** <what changed that makes this solvable>

## 4. Success metric
**V1 success =** <single measurable outcome with a target — not a list>
<1 line on how it's measured + when it's measured>

## 5. Out of scope
<bulleted list — features explicitly NOT in V1, with one-line "why not yet">

## 6. Visual direction
- **Palette:** <3–5 hex codes with names>
- **Typography:** <heading + body + mono fonts>
- **Reference products:** <2–3 named, with what to lift from each>
- **Anti-references:** <what NOT to copy — typically: AI slop fingerprints>

## 7. Feature list
(see Phase 2)

## 8. Screen list
(see Phase 3)

## 9. Landing page outline
(see Phase 4)

## 10. User flows
(see Phase 5)

## 11. Edge cases
(see Phase 6)

## 12. Open questions
<numbered list — every ambiguity. The reviewer answers these to unblock /architect.>
```

---

## Phase 2 — Feature list (the meat)

For EVERY feature in V1, fill this template. No shortcuts. Aim for 8–15 features for a typical V1.

```markdown
### F<n>. <Feature name>

**Problem solved:** <one sentence>
**User:** <which persona uses this — if everyone, say "all">
**Surfaces in:** <screen names from §8 — must be at least one>
**Trigger:** <what causes this feature to be invoked — user click, schedule, event>
**Inputs:** <what data does it consume>
**Output:** <what does the user see / what changes>
**Golden path:** <3–5 step happy-case flow>
**Edge cases:** <bulleted — what breaks, what's empty, what fails>
**Success metric (this feature):** <how do you know it's working>
**V1 vs V1.1:** <if part is deferred, say so explicitly>
```

**Rules:**
- Every feature must map to ≥1 screen. If you can't name a screen, the feature isn't real yet — kick it to "out of scope" or define a screen.
- "Surfaces in" cannot be vague ("dashboard" is wrong; "Insights tab on /home" is right).
- If a feature is invisible (background sync, cron job), still include it — surfaces field becomes "no UI surface, runs every X minutes" and edge cases must cover failures.

---

## Phase 3 — Screen list

For EVERY screen in V1, fill this template. Including modals, drawers, empty states, error pages.

```markdown
### S<n>. <Screen name> — `<route>`

**Purpose:** <why this screen exists, in one sentence>
**Reachable from:** <what links/CTAs lead here>
**Primary CTA:** <the one thing the user is meant to do — must be ONE thing>
**Layout (top to bottom):**
1. <section> — <what it shows>
2. <section> — <what it shows>
3. ...

**States (every state must be defined):**
- **Empty** — first-time user, no data: <what shows, what CTA>
- **Loading** — data fetching: <skeleton / spinner / what's visible>
- **Populated** — happy case: <what's shown>
- **Error** — fetch failed / partial data: <what shows, recovery CTA>
- **Permission denied** — if applicable: <what shows>

**Responsive behavior:**
- Desktop (≥1024px): <key layout note>
- Tablet (768–1023): <if different>
- Mobile (<768): <key layout note — what stacks, what hides>

**Accessibility notes:** <focus order, ARIA needs, keyboard shortcuts>
```

---

## Phase 4 — Landing page outline

Even if this is an internal tool, write a landing/onboarding page outline. For external products, this is the marketing site.

```markdown
### Landing page (`/`)

**Headline:** <≤10 words, value prop, no buzzwords>
**Sub-headline:** <≤25 words, who + what + why now>
**Above-the-fold CTA:** <single button text + destination>

**Sections (in order):**
1. **Hero** — headline + sub + CTA + visual (describe the visual: hero image / product shot / animation)
2. **The problem** — 1 paragraph, concrete, names the pain
3. **How it works** — 3 steps with one-line each
4. **Features** — 4–6 cards, each with: icon hint, title, 1-line description (NO 3-column purple gradient slop)
5. **Social proof** — testimonial / logo bar / stat. If you don't have any, write a placeholder marked TODO.
6. **Pricing** — even if "free in V1," state it clearly
7. **FAQ** — 5 questions answering: who is this for, how do I get started, what data do you have, security, pricing
8. **Final CTA** — repeat above-the-fold CTA
9. **Footer** — legal, contact, social

**Copy tone:** <direct / professional / playful — be specific>
**Banned copy patterns:** Never write "Welcome to X", "Unlock the power of", "Streamline your workflow", "Transform your". Be specific to the product.
```

---

## Phase 5 — User flows

For each top-3 user journey, write a numbered flow. Examples: signup → first-feature, daily-active-loop, recovery-from-error.

```markdown
### Flow A: <name> (e.g. "First-time user signup → first insight")

1. User lands on `/` → sees hero, clicks <CTA>
2. → `/signup` → fills email + password OR Google OAuth
3. → `/connect` → onboarding screen, picks first SaaS to connect
4. → OAuth flow with provider
5. → callback → `/onboarding/syncing` (loading state until first sync completes)
6. → `/home` → first insight is shown above fold
7. **Time to value:** <X minutes / Y clicks>

**Failure branches:**
- OAuth denied → `/connect` with error toast, retry CTA
- Sync timeout (>60s) → email user "we'll let you know when it's ready"
- Empty data after sync → `/home` empty state with "your first sync didn't return data — here's why"
```

---

## Phase 6 — Edge cases

A flat list. If you can think of it, list it. The owner uses this list to spot what you forgot.

```markdown
- User has 0 records: <what shows>
- User has 100k records (perf): <what we do>
- Network goes offline mid-action: <recovery>
- Token expires mid-session: <re-auth flow>
- User's email already exists: <merge or block>
- User is on iOS Safari (most paranoid mobile browser): <known constraints>
- Right-to-left language (if i18n): <state if scoped out>
- Screen reader: <every interactive element labeled>
- Slow 3G: <what loads first, what's deferred>
- ...
```

---

## Phase 7 — Visual mocks (default ON, skip with `--no-visual`)

For every screen in §8 and the landing page, generate a lightweight HTML wireframe.

**Output:** `outputs/<slug>/prd/screens/<screen-route>.html` and `outputs/<slug>/prd/landing.html`

**Wireframe rules:**
- Single self-contained HTML file (no frameworks, no externals)
- Use the palette + typography from §6 (so reviewer sees real direction, not generic)
- Use real placeholder content matching the PRD (real headlines, real feature names) — not "Lorem ipsum"
- Show the **populated** state by default; add small toggles at the top of the page to switch to empty / loading / error states
- Mobile + desktop in one file using media queries — the reviewer can resize to see both
- NO purple gradients, NO generic 3-column feature grids, NO "Welcome to X" copy — see `static-site-standards.md`
- Each wireframe ≤ 250 lines of HTML+CSS — these are reviewable mocks, not finished sites

**Index page:** Generate `outputs/<slug>/prd/index.html` — a single page that lists all screens with thumbnails (or labelled buttons) so the reviewer can click through every screen + state combo in one place.

If `--no-visual` is passed, skip this phase and note in prd.md that visual mocks were deferred.

---

## Phase 8 — Output bundle

When complete, the directory structure should be:

```
outputs/<slug>/prd/
├── prd.md                          (the narrative PRD — sections 1-12)
├── index.html                      (clickable index of all screens + landing)
├── landing.html                    (landing page mock, all states)
└── screens/
    ├── home.html
    ├── connect.html
    ├── chat.html
    ├── account.html
    └── ...
```

Update `outputs/<slug>/state.json`:
- Append `"prd"` to `phases_done` only AFTER both prd.md exists AND prd-reviewer agent has returned PASS.

---

## Handoff

> **PRD bundle written.** Now dispatch the `prd-reviewer` agent against `outputs/<slug>/prd/`. On PASS, surface to owner with the index URL: `outputs/<slug>/prd/index.html`. Owner reviews, approves or sends a feedback list, then `/cto` proceeds to `/architect`.

---

## Rules

- **Exhaustive over short.** A PRD that misses a feature is a PRD that produces a broken build. If in doubt, include it.
- **Every feature → ≥1 screen.** No abstract features.
- **Every screen → all states defined.** Empty/loading/populated/error are mandatory; permission-denied where applicable.
- **No AI slop in mocks.** Apply `static-site-standards.md` rules — banned palettes, banned layouts, banned copy.
- **Real placeholder content.** Mocks must read like the actual product, not generic Lorem.
- **The reviewer is the head of product, not an engineer.** Write for them: features and outcomes, not architecture and APIs. Architecture comes in `/architect`.
- **Open questions are required.** A PRD with zero open questions is a PRD with hidden assumptions. List ≥3.
