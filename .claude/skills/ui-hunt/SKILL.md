---
name: ui-hunt
description: Research skill that finds best-in-class products in the category you're building, extracts what makes them exceptional, and produces a Reference Brief for use in /design-shotgun or static-site-replicator. The root cause of AI slop is building without a reference — this skill fixes that.
triggers:
  - /ui-hunt
args: "[what you're building — be specific: 'SaaS dashboard for logistics', 'mobile food delivery app', 'B2B invoicing tool']"
---

# UI Hunt

You are a design researcher. Your job is to find the best-designed products in this category, understand *why* they work, and produce a Reference Brief that gives the builder a specific, actionable design target — not a mood board.

Generic output is the enemy. "Clean and modern" is useless. "Inter at 14px/1.6 line-height with a #0F172A slate base and high-contrast CTAs" is useful.

---

## Phase 1 — Define the Category Precisely

Before searching, sharpen the input:

1. **What type of product is this exactly?** (e.g., not "dashboard" — "B2B SaaS analytics dashboard for ops teams")
2. **Who is the user?** (consumer vs. professional vs. developer — design language differs significantly)
3. **What is the primary action?** (read-heavy, write-heavy, real-time monitoring, exploration, onboarding)
4. **What context does this live in?** (web app, landing page, mobile app, internal tool)

If the input is vague, narrow it with one clarifying question before searching.

---

## Phase 2 — Research Best-in-Class Products

Search across multiple surfaces to find the actual best work in this category. Use all of these:

**Product discovery:**
- Web search: `best [category] app design [year]`
- Web search: `[category] product design inspiration`
- Web search: `site:dribbble.com [category] ui design`
- Web search: `[category] app awwwards`
- Web search: `[specific competitor names] design`

**Award and gallery sites:**
- Awwwards.com — best web design
- Godly.website — curated digital design
- Mobbin.com — mobile UI patterns (use for mobile categories)
- Pageflows.com — real onboarding/product flows
- Dribbble.com — interface design shots

**Direct competitors:**
- Search for the top 3-5 known products in the category
- Look at their actual product screenshots (search: `[product name] UI screenshots`, `[product name] dashboard design`)

Identify **5 candidates**, then narrow to **top 3** based on:
- Visual quality and craft (not just features)
- Relevance to the specific user type and context
- Recognition/awards (signals other designers validated the work)

---

## Phase 3 — Extract Design Intelligence

For each of the top 3 references, extract specific, usable design intelligence — not vague praise.

### Per-reference analysis

**Product name:** [name]
**URL / source:** [link or search result]
**Why it made the list:** [one sentence — the specific thing it does exceptionally well]

| Dimension | What they do | Why it works |
|-----------|-------------|--------------|
| Color palette | Primary: `#XXX`, Secondary: `#XXX`, Accent: `#XXX`, Background: `#XXX`, Text: `#XXX` | [e.g., "High contrast base with a single warm accent — reads as trustworthy, not playful"] |
| Typography | Headings: [font, weight, size], Body: [font, size, line-height] | [e.g., "Variable weight Inter creates hierarchy without needing multiple fonts"] |
| Layout pattern | [e.g., "Fixed left nav, fluid content area, right panel for context"] | [e.g., "Separates navigation from work area — user knows exactly where they are"] |
| Spacing rhythm | [e.g., "4px base unit, generous padding in cards (24px), tight lists (8px)"] | [e.g., "Density feels intentional — data-heavy without claustrophobia"] |
| Interaction signature | [e.g., "Instant feedback on every action, micro-animations on state changes"] | [e.g., "Makes the product feel alive without being distracting"] |
| Copy tone | [e.g., "Terse, action-oriented labels. No marketing in the UI."] | [e.g., "Respects the user's time — they're here to work"] |
| Differentiator | [the one thing this product does in its UI that competitors don't] | [why it matters] |

---

## Phase 4 — Synthesize the Reference Brief

Produce a single synthesis — the design target for this build.

---

### Reference Brief: [Product Category]

**Top 3 references:**
1. [Product name] — [what to steal from it]
2. [Product name] — [what to steal from it]
3. [Product name] — [what to steal from it]

**Recommended palette:**
```
Base background:  #XXXXXX  ([description, e.g., "off-white, not pure white"])
Primary surface:  #XXXXXX  ([description])
Border / divider: #XXXXXX  ([description])
Primary text:     #XXXXXX  ([description])
Secondary text:   #XXXXXX  ([description])
Accent / CTA:     #XXXXXX  ([description])
```
*Rationale: [1-2 sentences on why this palette fits the product and user]*

**Typography:**
```
Headings: [font name], [weight range], [size scale e.g., "clamp(24px, 4vw, 48px)"]
Body:     [font name], [size], [line-height]
UI / labels: [font name or same], [size], [weight]
CDN: [Google Fonts or similar link]
```
*Rationale: [why these fonts fit the product context]*

**Layout archetype:**
[Describe the core layout pattern in plain English: how is space divided, where does the primary content live, how does navigation work]

**Spacing system:**
```
Base unit: [Xpx]
Card padding: [Xpx]
Section gap: [Xpx]
List item gap: [Xpx]
```

**Tone of voice (for copy):**
[How copy should sound. Specific adjectives + example of good vs. bad phrasing for this product]

**Key UX decisions to adopt:**
- [Specific decision from the references — e.g., "Always show counts next to tabs so user knows what's waiting"]
- [Another specific decision]
- [Another]

---

## Phase 5 — Anti-Pattern List

What do the *worst* products in this category look like? List the design mistakes that make products in this space feel cheap, confusing, or untrustworthy.

**Anti-patterns for [category]:**
- [e.g., "Overloading the dashboard with metrics nobody asked for — shows data instead of insight"]
- [e.g., "Purple/blue SaaS gradient header — every B2B tool looks like this now"]
- [e.g., "Generic stock photos of handshakes and laptops in hero sections"]
- [e.g., "Tables with no visual hierarchy — equal weight on everything"]
- [e.g., "CTAs that say 'Get Started' instead of describing the specific action"]

Add 5-8 anti-patterns specific to this category. Generic anti-patterns (from builder-ethos rules) are already enforced — only add category-specific ones here.

---

## Output Format

Deliver in this order:

1. **Category sharpened** — your refined understanding of what's being built
2. **Top 3 references** — per-reference analysis table (Phase 3)
3. **Reference Brief** — the synthesized design target (Phase 4)
4. **Anti-pattern list** — what to avoid (Phase 5)
5. **Handoff line:**

> **Reference Brief ready.** Hand this to `/design-shotgun` to generate variants against this target, or pass it directly to `/static-site-replicator` or `/execute` as the design specification.

---

## Rules

- **Be specific, never vague.** "Nice typography" is noise. "Inter 600 at 32px with -0.5px tracking" is signal.
- **Cite real products.** Don't invent imaginary references. If you can't find a strong reference after searching, say so and explain what the closest thing is.
- **Steal like an artist.** The goal is not to copy — it's to understand what principles make something work, then apply those principles.
- **One palette.** Don't give the user three palettes to choose from — synthesize one clear recommendation with a rationale.
- **Anti-patterns must be category-specific.** Generic slop rules are in builder-ethos. This list is for the unique failure modes of this category.
- **No mood board URLs.** A URL list is not a Reference Brief. Extract the intelligence, don't outsource the thinking.
