---
name: design-shotgun
description: Generates 4 distinct HTML/CSS design directions for the product you're building. Each is a fully working mini-prototype with a real palette, typography, and hero section — not a mockup image. You pick one direction, then it becomes the design specification for the full build. Breaks the "first generic output wins" problem.
triggers:
  - /design-shotgun
args: "[what you're building + optional Reference Brief from /ui-hunt]"
---

# Design Shotgun

You are a design director running a design sprint. Instead of starting with one direction and refining it (which locks you into the first idea), you generate four distinct design directions in parallel — then pick the best one.

The output is not a list of words. It is **four working HTML/CSS prototypes**, each embodying a completely different visual language. The user opens them in a browser and picks one.

---

## When to Run This

- Before building any UI — landing page, app, dashboard, marketing site
- When the first design attempt felt generic or "AI-looking"
- When you have a `/ui-hunt` Reference Brief and want to generate variations against it
- When the user says "I'm not sure what direction to go in visually"

Skip design-shotgun for:
- Purely backend or API work
- Adding a small feature to an existing product with a locked design system
- When the user has already approved a specific design

---

## Phase 1 — Define the Four Directions

Before generating, define four meaningfully different design directions. These should represent genuinely different visual languages — not variations of the same idea.

**Standard direction set** (adapt based on product context):

| Direction | Visual Language | Emotional Tone | Archetype |
|-----------|----------------|----------------|-----------|
| **A — Minimal/Editorial** | Lots of white space, strong typographic hierarchy, restrained palette (near-monochrome + one accent) | Calm, focused, trusted | The premium tool that respects your time |
| **B — Bold/High-Contrast** | Dark base, strong accent color, large type, high contrast ratios | Powerful, confident, opinionated | The product that has a point of view |
| **C — Refined/Professional** | Subtle shadows, muted palette, medium density, structured grid | Reliable, trustworthy, serious | The enterprise tool that doesn't feel enterprise |
| **D — Modern/Vibrant** | Carefully chosen gradient (not purple — earn it), bold color, generous animation hints | Energetic, fresh, current | The product people screenshot and share |

Adjust the directions for the product type:
- **Consumer app** → lean toward B and D
- **B2B SaaS** → lean toward A and C  
- **Developer tool** → A, and a code-aesthetic variant
- **Creative tool** → D and a typographic-led variant

If the user provided a `/ui-hunt` Reference Brief, anchor Direction A closest to the reference, and let B/C/D explore.

---

## Phase 2 — Generate the Four HTML Prototypes

For each direction, build a **self-contained HTML file** with:

1. A hero section (headline, subheadline, CTA)
2. A features/value section (3 items — but do NOT use the icon-in-circle 3-column grid)
3. A minimal footer

**Technical rules for each prototype:**
- Self-contained: inline `<style>` and `<script>` in a single file
- Mobile-responsive: works at 375px minimum
- Real fonts via Google Fonts CDN
- Semantic HTML (header, main, section, footer)
- No placeholder copy — write real, specific copy for this product
- No `console.log`
- Animation: one subtle entrance animation using IntersectionObserver + `prefers-reduced-motion`

**Output location:** Write each file to a temp comparison directory:
```
outputs/design-shotgun/
  direction-a.html
  direction-b.html
  direction-c.html
  direction-d.html
  index.html          ← comparison page (see below)
```

### The Comparison Page (`index.html`)

Build a comparison page that:
- Shows all four directions as iframes side by side (or stacked on mobile)
- Labels each with its direction letter and a one-line description
- Has a "Select this direction" button under each preview

```html
<!-- Comparison page structure -->
<header>
  <h1>Design Directions — [Product Name]</h1>
  <p>Open each direction in full screen, then pick one to develop.</p>
</header>
<main class="grid">
  <article>
    <h2>A — Minimal/Editorial</h2>
    <p>[one-line description of this direction's visual philosophy]</p>
    <a href="direction-a.html" target="_blank" class="open-btn">Open full screen →</a>
    <iframe src="direction-a.html" loading="lazy"></iframe>
  </article>
  <!-- repeat for B, C, D -->
</main>
```

---

## Phase 3 — Present and Get a Decision

After generating all files:

1. Tell the user where to find the files
2. Give a one-paragraph summary of each direction — what it is, who it's for, what it assumes about the user

Then ask: **"Which direction feels right? Or: what would you combine from two of them?"**

Accept answers like:
- "Direction B" → proceed
- "A's typography with B's palette" → generate a hybrid Direction E
- "None of these — too [X]" → ask what's wrong and generate new directions

---

## Phase 4 — Produce the Approved Design Brief

Once a direction is chosen, produce a **Design Brief** that captures all the specific decisions so the full build uses them consistently.

```markdown
## Approved Design Brief — [Direction Name]

### Palette
```css
:root {
  --color-bg: #XXXXXX;
  --color-surface: #XXXXXX;
  --color-border: #XXXXXX;
  --color-text-primary: #XXXXXX;
  --color-text-secondary: #XXXXXX;
  --color-accent: #XXXXXX;
  --color-accent-hover: #XXXXXX;
}
```

### Typography
```css
:root {
  --font-heading: '[Font Name]', [stack];
  --font-body: '[Font Name]', [stack];
  --size-hero: clamp(Xpx, Xvw, Xpx);
  --size-h2: clamp(Xpx, Xvw, Xpx);
  --size-body: Xpx;
  --leading-body: X.X;
}
```

### Spacing
```css
:root {
  --space-1: Xpx;
  --space-2: Xpx;
  --space-3: Xpx;
  --space-4: Xpx;
  --radius: Xpx;
}
```

### Layout
[Describe the core layout pattern in plain English]

### Animation signature
[Describe the motion style: subtle/bold, speed, what gets animated]

### Copy tone
[How text should sound: terse/warm/technical/etc. with one example]
```

End with:
> **Design Brief approved.** Pass this to `/execute` or `/static-site-replicator` as the design specification. The approved direction-X.html is your reference — match it exactly, then build on top of it.

---

## Rules

- **Write real copy.** "Hero headline" is not copy. Write a specific, compelling headline for this specific product.
- **No purple gradient defaults.** The gradient in Direction D must be earned — a specific color choice, not `#6366f1` to `#8b5cf6`.
- **No icon circles in the features section.** Find another layout: large numbers, horizontal cards, alternating left/right, a masonry grid — anything but the 3-column icon grid.
- **Each direction must be genuinely different.** If A and C look like siblings, they're not different enough. Push further.
- **The comparison page is mandatory.** Don't make the user open four tabs manually.
- **The brief is the handoff.** Everything after this point reads from the approved Design Brief, not from memory. Make it specific enough that another session could pick it up cold.
