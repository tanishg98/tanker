# Advisor Review — Shiprocket Visibl PRD v2.1

**Artifact:** ~/Documents/notion-export/visibl-prd.md
**Authored by:** Opus 4.7
**Reviewed by:** Sonnet 4.6
**Date:** 2026-04-23

---

## 1. Fundamental Disagreements

**Claim: "Peec already has 115 lang; Hindi is a week of work" (Risk section)**
Wrong framing. Peec's 115 languages apply to UI-scraping methodology. Building Hindi prompt tracking that is actually useful to Indian sellers requires a prompt corpus in Hindi, validation that Indian LLMs respond coherently to Hindi product queries, and QA. "A week of work" undersells it and lulls the team into treating Hindi as low-urgency when it's a meaningful competitor catch-up vector.

**Claim: "Auto-competitor discovery from brand/URL" is a white-space moat**
The matrix says Profound has partial coverage. The PRD acknowledges this in the feature table but lists it among defensible moats in Section 1 without caveat. Can't simultaneously be a "Visibl moat" and a feature Profound already partially does. Reframe as "SMB-accessible version of Profound's enterprise feature."

**Claim: "Review acquisition workflow" belongs in Module 1 (FREE)**
Auto-nudging sellers' customers via WhatsApp post-delivery is a cross-team dependency (Engage 360/Interakt), a deliverability risk, and a seller trust risk. Putting it in free tier is premature. Gate behind Growth and validate in beta.

## 2. Missing Content

- **No unit economics.** ₹15–25L/mo stated but never sized per-seller. Weekly LLM query runs at scale = real API/scraping cost per seller per week. Without this, pricing table is invented numbers.
- **No go-to-market plan.** 50,000-seller score generation mechanic only implied in positioning.
- **No competitor response section.** Peec adding Hindi is trivial once they see Visibl. No risk framing for public-launch response.

## 3. Unsupported Assumptions

- **"≥15% buyers used LLMs in last 5 purchases"** — false precision. Where does 15% come from? This threshold determines GO/NO-GO on the whole build.
- **"≥10% free-to-paid within 30 days"** — Indian SMB SaaS benchmarks are 2–5%. 10% would be exceptional. Looks wrong to an investor.
- **WhatsApp alerts as differentiator** — assumes sellers want them; Engage 360 adoption rate is itself unresolved. If low, the "moat" is a non-feature.

## 4. Scope Issues

- **Referrer pixel in free tier is over-specified.** Trigger by Module 4 upgrade, not as a Module 1 prereq.
- **Slack alerts in v1 is filler.** "Trivial to add" = add later. Each feature is QA + settings + docs + support. Cut to v1.5.
- **GDPR in v1** — Indian D2C selling to India doesn't need it. Move to v1.5.
- **Module 4 in v1 is too ambitious.** Both headline features (return-adjusted attribution, order-level data) are marked BLOCKED. A module whose two headline features are gated on pending org decisions should not be v1. Defer to v1.5 with data signoff as the trigger.

## 5. Matrix → PRD Mapping Audit (10 rows)

| # | Row | PRD decision | Sonnet's call |
|---|---|---|---|
| 1 | Tracks Claude | v1.5 | **MISMATCH** — 20+/31 track Claude, incl. all Tier 1. Should be v1. |
| 2 | Sentiment analysis | v1.5 | Consistent |
| 3 | Auto-competitor discovery | v1 (white-space moat) | Consistent feature-level; positioning needs caveat |
| 4 | AXP | v2+ | Correct |
| 5 | Answer gap → article gen | v1.5 | Defensible but PRD should acknowledge enterprise-tier gap |
| 6 | Multi-brand dashboard | v2+ | Consistent |
| 7 | PDF export | v1.5 | **MISMATCH** — 74% coverage, table-stakes. Should be v1. |
| 8 | Proprietary prompt volume panel | SKIP | Correct |
| 9 | RegGuard | v2+ | Correct |
| 10 | GMV-weighted optimization | v1 | **MISMATCH** — depends on order-level data which is BLOCKED. Same dependency, different flag. |

## 6. What the PRD Got Right

- Validation gate structure (Section 5) — genuinely good, thresholds actionable
- Flagging internal Visibl overlap as HIGH risk — honest, most PRDs bury this
- Deferring Module 3 entirely — correct; content gen without brand voice ships slop
- Matrix-to-decision discipline — prevents scope creep
- Identifying referrer pixel as the missing Module 4 dependency — real catch

## 7. Top 3 Changes

1. **Move Module 4 to v1.5, reframe v1 around the validated modules.** Module 4's key features are blocked on org decisions. Committing in v1 sets up a broken ship or a delay. Make data signoff the trigger for v1.5 Module 4 launch. Simplifies v1 pitch: score + monitor first, revenue proof after.

2. **Add unit economics before any build decision.** Per-seller cost must be sized (prompts × platforms × weekly cadence × scraping cost) vs ₹999 ARPU. If math doesn't work at 10K sellers, no feature work fixes it. Cannot go to Saahil without this.

3. **Fix PDF export and Claude tracking deferrals.** PDF is 74% table-stakes; Claude is 65%+. Both cheap to include. Moving to v1 makes launch feel complete rather than cheap.
