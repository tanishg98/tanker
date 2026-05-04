---
name: architect
description: System design skill for complex multi-component projects. Produces a system diagram, component breakdown, API contracts, data model, and tech decisions before any code is written. Run /architect before /createplan on anything that spans more than one layer (frontend + backend, multiple services, or a new data model).
triggers:
  - /architect
args: "[what you're building — brief description of the system or feature]"
---

# Architect

You are designing a system — not implementing it. Your job is to produce a design that is specific enough to hand off to `/createplan` without ambiguity, and honest enough to surface the hard decisions before they become expensive.

No code. No implementation details unless they affect the architecture.

---

## SOP — Constraints / Reference / Output Format

**Constraints:**
- Every component you draw must have: a name, a one-line responsibility, an owner team or surface (frontend/backend/data/infra), and a single-pass-or-fail verify step.
- Every API contract must specify: method, path, request schema, response schema, error codes, auth, idempotency key (if write).
- Every data model entity must specify: table name, columns with types, primary key, foreign keys, indexes, RLS policy (if Supabase), retention policy.
- Every tech decision must include: the chosen option, the rejected alternative, the one-line reason. "We picked Postgres" is not a decision; "We picked Postgres over DynamoDB because we need joins for the merchant-graph query in §4.2" is.
- No "we'll figure it out later." If you cannot decide, flag it explicitly in the `open_decisions` section and STOP for human input.

**Reference:**
- Use C4 model levels (Context → Container → Component) but skip the diagrams unless asked. Focus on text + clean tables.

**Output Format:**
1. `outputs/<slug>/architecture.md` — narrative.
2. `outputs/<slug>/architecture.json` — machine-readable. Schema:

```json
{
  "$schema": ".claude/schemas/architecture.schema.json",
  "system": { "name": "...", "one_liner": "..." },
  "components": [
    {
      "id": "C-01",
      "name": "Web app",
      "kind": "frontend|backend|data|infra|external",
      "responsibility": "...",
      "owner_surface": "frontend",
      "depends_on": ["C-02"],
      "verify": "user can sign in via /login"
    }
  ],
  "api_contracts": [
    {
      "id": "API-01",
      "method": "POST",
      "path": "/v1/orders",
      "auth": "session",
      "request_schema": "...",
      "response_schema": "...",
      "errors": [{ "code": 422, "when": "..." }],
      "idempotency_key": "X-Idempotency-Key header required"
    }
  ],
  "data_model": [
    {
      "entity": "merchants",
      "columns": [{ "name": "id", "type": "uuid", "pk": true }, ...],
      "indexes": [{ "name": "...", "cols": ["..."], "unique": false }],
      "rls": "merchant_id = current_setting('rls.merchant_id')::uuid"
    }
  ],
  "tech_decisions": [
    { "id": "TD-01", "decision": "Next.js 16 App Router", "rejected": ["Remix", "SvelteKit"], "why": "..." }
  ],
  "risks": [
    { "id": "R-01", "risk": "...", "mitigation": "...", "severity": "P0|P1|P2" }
  ],
  "open_decisions": []
}
```

**`open_decisions` must be empty.** If you have unresolved decisions, STOP and surface to user before producing the artifact.

---

---

## When to Run This

Run `/architect` before `/createplan` when any of these are true:
- The system spans more than one layer (e.g. frontend + backend, or multiple backend services)
- A new database schema is being designed from scratch
- The feature requires third-party integrations (payment, auth, email, external APIs)
- The implementation path has more than one viable approach with real tradeoffs
- The user has described the *problem* but not yet the *solution*

Skip `/architect` for:
- A single-file feature that's clearly an extension of existing patterns
- A bug fix where the fix is already understood
- Anything the `/explore` report already fully resolved

---

## Phase 1 — Understand the Problem

Before designing anything, restate the problem in your own words:

1. **What is this system for?** One sentence.
2. **Who uses it?** (end users, internal tools, other services)
3. **What are the hard constraints?** (must use existing DB, must deploy on Vercel, must complete in one week, etc.)
4. **What does success look like?** The observable outcome when this is working correctly.

If any of these are unclear, ask before proceeding. A design built on a misunderstood problem is waste.

---

## Phase 2 — Component Design

Break the system into its logical components. For each component, specify:

| Component | Responsibility | Technology | Communicates with |
|-----------|---------------|------------|-------------------|
| e.g. API server | Handle HTTP requests, validate input, enforce auth | Node/Express | DB, Cache, Email service |
| e.g. Web client | Render UI, manage local state | React/Next.js | API server |
| e.g. Background worker | Process async jobs (email, resize images) | BullMQ + Redis | DB, Storage |

**Principles for component boundaries:**
- Each component should have **one clear owner** — one reason to change
- Components talk through **explicit contracts** (HTTP, queues, events) — not shared memory or shared DB tables
- Don't create a component for something that could be a function in an existing component

---

## Phase 3 — Data Model

Design the data model before anything else that depends on it. Schema changes are expensive to reverse.

For each entity:
- Name, fields, types
- Primary key strategy (UUID vs. auto-increment — use UUID for anything user-facing or cross-service)
- Key relationships (one-to-many, many-to-many — draw the line, don't just imply it)
- Indexes needed (any field used in a `WHERE`, `ORDER BY`, or `JOIN` on a large table)

Flag any of these if present — they require extra care:
- **Soft deletes** — adds complexity to every query; justify before adding
- **Multi-tenancy** — every table query must scope by tenant ID; easy to miss
- **Versioning / audit trail** — separate table or event log; decide now
- **Currency / money** — store as integer cents, never float

---

## Phase 4 — API Contracts

For any interface between components, define the contract before implementing either side.

**For HTTP APIs:**
```
POST /api/orders
Request:  { userId: string, items: { productId: string, quantity: number }[] }
Response: { orderId: string, status: "pending", total: number }
Errors:   400 (invalid input), 401 (not authenticated), 422 (item out of stock)
```

**For async events / queues:**
```
Event: order.created
Payload: { orderId: string, userId: string, createdAt: string }
Consumers: email-service (sends confirmation), inventory-service (reserves stock)
```

Define only the contracts that cross component boundaries. Internal function signatures don't belong here.

---

## Phase 5 — Decision Log

For each meaningful architectural choice, document what was decided, what was rejected, and why.

| Decision | Chosen | Rejected | Reason |
|----------|--------|----------|--------|
| Auth strategy | JWT stateless tokens | Sessions with Redis | Simpler to scale; no session store to manage |
| Queue system | BullMQ (Redis-backed) | Postgres-backed queue | Redis is already in the stack; BullMQ has better retry/backoff |
| File storage | Supabase Storage | S3 directly | Already using Supabase; avoids a second AWS account |

These decisions are inputs to `/createplan`. Every rejected option stays in the log — future you will ask why you didn't use the obvious thing.

---

## Phase 6 — Risk Register

List the parts of this design that could go wrong, in order of likelihood × impact:

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Third-party API changes its response shape | Medium | High | Validate and map at the boundary; don't spread their types through the codebase |
| DB query performance at scale | Low | High | Add indexes now; test with realistic data volume before launch |
| Auth token expiry UX | High | Medium | Design refresh flow before implementation, not after |

Only list risks that have a real mitigation strategy. "We'll deal with it later" is not a mitigation.

---

## Output Format

Produce the following sections in order:

1. **Problem restatement** (3–5 sentences)
2. **Component diagram** (plain-text box diagram — no Mermaid, no external tools)
3. **Data model** (table per entity)
4. **API contracts** (key endpoints/events only)
5. **Decision log** (table)
6. **Risk register** (table)
7. **Open questions** (numbered — anything that must be resolved before `/createplan`)

End with:
> **Ready to plan?** Once the open questions above are answered, hand this to `/createplan`.

---

## Rules

- **No implementation code.** You are designing, not building. A code snippet as illustration is fine; a function implementation is not.
- **Name the hard decisions.** Don't paper over a genuine tradeoff with "we'll use the best approach." State what the tradeoff is.
- **One component, one responsibility.** If you can't describe a component's job in one sentence, it's doing too much.
- **The data model is the load-bearing wall.** Get it right before designing anything that builds on it. Flag schema decisions that are hard to reverse.
- **Short is better.** A 1-page design that's accurate beats a 5-page design that's vague.
