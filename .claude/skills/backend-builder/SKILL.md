---
name: backend-builder
description: Build backend APIs, servers, and databases. Covers Node/Express/Fastify, FastAPI, Supabase, auth patterns, error handling, and security. Trigger when the user needs a server, API endpoint, database schema, or backend integration.
triggers:
  - /backend-builder
args: "[what to build — REST API | auth layer | DB schema | full backend | specific endpoint]"
---

# Backend Builder

You are building a production-ready backend. Not a prototype — a backend that handles errors, validates inputs, secures its routes, and won't embarrass you when it hits real traffic.

---

## Phase 0 — Choose Stack

Before writing a line, confirm the tech stack. Ask if not specified.

**Node.js options:**
- **Express** — default choice; mature, minimal, well-understood. Use this unless there's a reason not to.
- **Fastify** — when raw performance matters (high-throughput APIs). Schema-first, ~2× faster than Express at scale.
- **Hono** — when deploying to edge runtimes (Cloudflare Workers, Deno). Tiny bundle, Web Standard APIs.

**Python options:**
- **FastAPI** — async-first, automatic OpenAPI docs, Pydantic validation. Default for Python backends.
- **Flask** — when you need something minimal or the project already uses it.

**Backend-as-a-service:**
- **Supabase** — when you need Postgres + auth + realtime + storage without managing infra. Use the `@supabase/supabase-js` client or direct SQL via `pg`.

**Decision rule:** match the existing tech stack first. Only introduce a new language/runtime if the project has no backend yet and there's a clear reason to choose it.

---

## Phase 1 — Scaffold

### Project structure (Node/Express example)
```
src/
├── routes/          ← one file per resource (users.ts, orders.ts)
├── middleware/      ← auth, error handler, request logger
├── services/        ← business logic, no HTTP concerns
├── db/              ← queries, migrations, schema
├── lib/             ← shared utilities (e.g. mailer, storage client)
└── index.ts         ← app setup, listen
```

### Startup checklist
- [ ] Environment variables loaded from `.env` via `dotenv` (Node) or `python-dotenv` (Python) — never hardcoded
- [ ] `.env.example` committed with all required keys listed (no values)
- [ ] `.env` in `.gitignore`
- [ ] CORS configured — explicit allowed origins, not `*` unless this is a public API
- [ ] Request body size limit set (default Express: 100kb — raise if needed, never `Infinity`)
- [ ] HTTP server only — no HTTPS in the app itself (terminate TLS at the load balancer/proxy)

---

## Phase 2 — Core Patterns

### Routes
- Group by resource, not by HTTP method
- Route handlers are thin: validate input → call service → return response
- Business logic lives in services, never in route handlers

```typescript
// Good — handler delegates to service
router.post('/orders', authenticate, async (req, res) => {
  const parsed = CreateOrderSchema.safeParse(req.body)
  if (!parsed.success) return res.status(400).json({ error: parsed.error.flatten() })
  const order = await orderService.create(parsed.data, req.user.id)
  res.status(201).json(order)
})
```

### Input validation
- **Always validate at the route level**, before calling services
- Node: use `zod` — define a schema, call `.safeParse()`, return 400 on failure with the error detail
- Python/FastAPI: use Pydantic models — declare the type, FastAPI validates automatically
- Never trust `req.body`, query params, or path params without validation

### Auth patterns
Three layers — implement all three:

**1. Authentication** — is this a valid user?
- JWT: verify signature + expiry in middleware before any protected route
- Session: validate session ID against store (Redis or DB) — never trust client-side session data

**2. Authorisation** — can this user do this thing?
- Check ownership server-side: `WHERE id = ? AND user_id = ?`
- Never trust a user-supplied `userId` to scope their own data — scope it from the verified token
- Role checks happen in the service layer, not the client

**3. Rate limiting**
- Apply to auth routes (login, register, password reset) — minimum 5 req/minute per IP
- Apply to all unauthenticated routes at a higher threshold (100 req/minute)
- Use `express-rate-limit` (Node) or `slowapi` (FastAPI)

### Error handling

**Node — central error middleware (add as the last `app.use`):**
```typescript
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err)  // replace with your logger
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({ error: err.message })
  }
  res.status(500).json({ error: 'Internal server error' })
})
```

**Rules:**
- Never expose stack traces or internal error messages to the client in production
- Use a typed `AppError` class with `statusCode` for expected errors (404, 400, 403)
- Unexpected errors always return 500 with a generic message
- Log every 5xx with full context (route, user ID if available, request body shape)

### Database (Postgres / Supabase)

**Query safety:**
- Parameterised queries only — never string-interpolate user input into SQL
- Use an ORM (Prisma, Drizzle) or a query builder (Knex) — raw SQL only for complex queries the ORM can't express

**Connection management:**
- Use a connection pool — never create a new connection per request
- Set `max` pool size to match your DB's connection limit (Supabase free: 15)
- Close the pool gracefully on `SIGTERM`

**Migrations:**
- Schema changes live in migration files, not applied manually
- Migrations are run automatically on deploy, not manually

**Supabase-specific:**
- Enable Row Level Security (RLS) on every table with user data
- Define policies that match your auth model — don't disable RLS as a shortcut
- Use service role key only in server-side code — never expose to the client

---

## Phase 3 — Security Checklist

Run this before marking any backend complete:

- [ ] No secrets in code or version control (`process.env.*` only)
- [ ] All user-facing routes validate input with zod/Pydantic
- [ ] Auth routes are rate-limited
- [ ] Ownership checks are server-side (`WHERE user_id = req.user.id`)
- [ ] SQL queries are parameterised — no string interpolation
- [ ] Error responses don't leak stack traces or internal details
- [ ] CORS origins are explicit, not `*` (unless intentionally public)
- [ ] File uploads (if any): type validated, size capped, stored outside webroot
- [ ] Dependencies scanned: `npm audit` / `pip audit` — no HIGH/CRITICAL unresolved
- [ ] Health check endpoint exists (`GET /health → 200 OK`) for load balancer / uptime monitoring

---

## Phase 4 — Pre-Handoff

Before calling the backend "done":

1. All routes have been manually tested (curl or a tool like Bruno/Insomnia) — not just "it compiles"
2. Error paths tested: invalid input → correct 400, missing auth → 401, wrong ownership → 403
3. `.env.example` is up to date with every variable the app reads
4. At least one integration test covers the critical path (the thing that breaks the business if it's wrong)

---

## Rules

- **Services own logic, routes own HTTP.** A service function should be callable without an HTTP context.
- **Validate at the boundary.** Once data is inside a service, it can be trusted. Don't re-validate internal calls.
- **Fail loudly in development, gracefully in production.** `NODE_ENV=development` can expose error details; production never does.
- **Don't implement your own crypto.** Use bcrypt for passwords, a signed JWT library for tokens, an established OAuth library for third-party auth.
- **Idempotency for mutations.** Any endpoint that creates or modifies data should handle duplicate requests gracefully — especially webhooks and payment callbacks.
