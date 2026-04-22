---
name: monitor
description: Post-ship observability skill. Sets up error tracking, analytics, uptime monitoring, and logging for a deployed project. Run after /deploy, or when something breaks in production and you realise you can't see what's happening.
triggers:
  - /monitor
args: "[what to monitor — errors | analytics | uptime | logging | all] [stack — node | python | browser | next]"
---

# Monitor

You are wiring up visibility into a running system. The goal: when something breaks in production, you find out before your users do — and you have enough information to fix it fast.

---

## The Four Pillars

| Pillar | What it answers | Tool |
|--------|----------------|------|
| **Error tracking** | What broke, where, for whom | Sentry |
| **Analytics** | Who is using what, conversion, retention | PostHog or Plausible |
| **Uptime monitoring** | Is the service reachable right now | Better Uptime or UptimeRobot |
| **Logging** | What happened in what order | Structured logs → Axiom or Logtail |

Don't set up all four at once for a v1. Priority order:
1. Error tracking (non-negotiable — you're blind without it)
2. Uptime monitoring (5-minute setup, catches outages)
3. Logging (critical for backends; optional for static sites)
4. Analytics (add when you need to make product decisions)

---

## Phase 1 — Error Tracking (Sentry)

Sentry captures unhandled exceptions, gives you stack traces, user context, and a timeline of what happened before the crash.

### Setup — Node.js / Express

```bash
npm install @sentry/node
```

```typescript
// src/instrument.ts — import this BEFORE everything else in index.ts
import * as Sentry from '@sentry/node'

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,  // 10% of requests get performance traces
})
```

```typescript
// In Express: add AFTER all routes, BEFORE your own error handler
app.use(Sentry.Handlers.errorHandler())
```

### Setup — Next.js / React (browser)

```bash
npx @sentry/wizard@latest -i nextjs
```
The wizard configures `sentry.client.config.ts` and `sentry.server.config.ts` automatically.

### Setup — Python / FastAPI

```bash
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk
sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    environment=os.environ.get("ENV", "production"),
    traces_sample_rate=0.1,
)
```

### Configuration checklist
- [ ] `SENTRY_DSN` in environment variables (get from Sentry dashboard → Project → Settings → Client Keys)
- [ ] `environment` set correctly (`production` vs `staging`) — keeps alerts separate
- [ ] Source maps uploaded for minified JS (Sentry webpack/Vite plugin — required for readable stack traces in frontend)
- [ ] Alert rule: email/Slack on first occurrence of a new error
- [ ] Ignored errors configured: known non-issues like `ResizeObserver loop limit exceeded` (browser noise)

### What to attach to errors
Always include enough context to reproduce the issue:
```typescript
Sentry.setUser({ id: req.user?.id })  // which user triggered it
Sentry.setTag('route', req.path)      // which route
Sentry.setContext('request', {        // what data was involved
  body: req.body,
  query: req.query,
})
```

---

## Phase 2 — Uptime Monitoring

Uptime monitoring pings your health check endpoint every minute and alerts you if it stops responding.

### Better Uptime (recommended — free tier is generous)
1. Sign up at betteruptime.com
2. Add monitor: your domain + `/health` endpoint
3. Check interval: 3 minutes
4. Alert: email immediately, then escalate to phone if down > 5 minutes
5. Add a status page (public URL your users can bookmark)

### UptimeRobot (alternative, free)
1. Add HTTP(s) monitor → `https://yourdomain.com/health`
2. Monitoring interval: 5 minutes (free tier limit)
3. Alert contact: email

**What to monitor:**
- Main app URL (`/health`)
- Any critical downstream dependencies your app calls (payment provider, auth service)
- If you have a background worker: add a heartbeat endpoint it pings every N minutes

---

## Phase 3 — Structured Logging

Logs are only useful if they're structured (JSON), searchable, and retained long enough to debug an incident.

### Node.js — use `pino` (fast, structured by default)

```bash
npm install pino pino-pretty
```

```typescript
import pino from 'pino'

export const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',
  // In production: output raw JSON. In dev: pretty-print.
  transport: process.env.NODE_ENV !== 'production'
    ? { target: 'pino-pretty' }
    : undefined,
})
```

**Log levels — use them correctly:**
- `logger.error()` — something broke; needs attention
- `logger.warn()` — something unexpected happened but the request succeeded
- `logger.info()` — normal operation milestones (server started, job completed)
- `logger.debug()` — detailed tracing for development; **disabled in production**

**What every request log should include:**
```typescript
logger.info({
  method: req.method,
  path: req.path,
  statusCode: res.statusCode,
  durationMs: Date.now() - startTime,
  userId: req.user?.id,
})
```

### Log shipping (production)

Logs on the container's stdout are lost when the container restarts. Ship them to a log aggregator:

- **Axiom** — generous free tier, good UI, SQL-like query language. Install via `pino-axiom` transport.
- **Logtail (Better Stack)** — integrates with Better Uptime (same company), easy setup.
- **Railway / Fly built-in** — both platforms surface recent logs in their dashboard; good enough for small projects.

---

## Phase 4 — Analytics

Add analytics when you need to answer product questions: which features are used, where users drop off, what's converting.

### PostHog (recommended for product analytics)
- Self-hostable or cloud
- Session recording, funnel analysis, feature flags
- No cookie banner required if you disable cross-site tracking

```bash
npm install posthog-js  # browser
npm install posthog-node  # server-side
```

```typescript
// Browser: initialise once on app load
posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY, {
  api_host: 'https://app.posthog.com',
  capture_pageview: true,
})

// Track a custom event
posthog.capture('order_completed', { orderId, value: totalCents / 100 })
```

### Plausible (recommended for simple traffic analytics)
- Privacy-first (no cookies, GDPR-compliant out of the box)
- One script tag, no configuration
- Good for: page views, referrers, geography, device. Not good for: complex funnels

```html
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

**When to use which:**
- Need to understand user behaviour / funnels / feature adoption → PostHog
- Just need traffic numbers without cookie consent overhead → Plausible

---

## Phase 5 — Alerting Setup

Monitoring without alerting is just a dashboard nobody looks at.

**Minimum viable alerting:**

| Event | Alert channel | Urgency |
|-------|--------------|---------|
| New Sentry error (first occurrence) | Email | Low |
| Sentry error rate spike (>10 in 1 hour) | Slack + email | Medium |
| Uptime monitor fails | Email immediately | High |
| Uptime down >5 minutes | SMS / phone call | Critical |

**Slack integration:**
- Sentry: Settings → Integrations → Slack → configure per-project
- Better Uptime: Settings → Integrations → Slack

---

## Observability Checklist

Run before calling monitoring "done":

- [ ] Sentry installed, DSN configured, `environment` tag set correctly
- [ ] Test error confirmed in Sentry dashboard (trigger one deliberately)
- [ ] Source maps uploaded (for any minified/transpiled JS)
- [ ] Uptime monitor pinging `/health` and alert contact confirmed
- [ ] Logger in use (no bare `console.log` in production code)
- [ ] Log level is `info` in production (not `debug` — too noisy)
- [ ] At least one alert channel configured (email minimum)
- [ ] Status page URL shared with team

---

## Rules

- **Error tracking is not optional.** Every production deployment needs it. You will not remember to check dashboards. Errors must come to you.
- **Don't log sensitive data.** No passwords, tokens, full credit card numbers, or PII in logs. Mask or omit before logging.
- **Structured logs only in production.** Pretty-print is for development. JSON logs are parseable by tooling.
- **Test your alerts.** Before going live, trigger a test alert on every channel. An alert that silently fails is worse than no alert.
- **Set log retention.** Logs cost money. Set a retention policy (30 days is usually sufficient) rather than keeping everything forever.
