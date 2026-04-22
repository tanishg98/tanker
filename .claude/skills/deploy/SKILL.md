---
name: deploy
description: Deployment skill covering Vercel, Railway, Fly.io, and Docker. Handles environment variable setup, CI/CD pipeline, health checks, and rollback strategy. Run after /execute when the build is ready to ship, or on a greenfield project to wire up deployment from the start.
triggers:
  - /deploy
args: "[platform — vercel | railway | fly | docker | auto-detect] [what — frontend | backend | fullstack | worker]"
---

# Deploy

You are wiring up a production deployment. The goal is a pipeline where: code merged to `main` → build passes → deployed automatically → health checked → rollback available if something breaks.

---

## Phase 0 — Choose Platform

If not specified, recommend based on what's being deployed:

| What | Recommended | Why |
|------|------------|-----|
| Static site / Next.js frontend | **Vercel** | Zero-config, edge CDN, preview deploys per PR |
| Node.js / Python API | **Railway** | Simple, Postgres included, no YAML config required |
| Anything needing persistent disk or custom ports | **Fly.io** | Real VMs, persistent volumes, global regions |
| Existing Docker workflow / self-host | **Docker + Compose** | Full control, runs anywhere |
| Frontend + backend, tight budget | **Railway** (both on one platform) | Simplest ops story |

If the project already has a deployed environment, don't change the platform — work within what exists.

---

## Phase 1 — Environment Variables

Before deploying, audit all environment variables the app reads.

**Checklist:**
- [ ] Every `process.env.*` / `os.environ[*]` reference is listed
- [ ] Variables are split by sensitivity:
  - **Public** (safe in frontend bundles): API base URLs, feature flags, public keys
  - **Secret** (never in client code): DB passwords, JWT secrets, API keys, webhook secrets
- [ ] `.env.example` is committed with all keys listed but no values
- [ ] `.env` (with real values) is in `.gitignore` — verify with `git status`
- [ ] No secrets in `git log` — if they were committed, rotate them now, then remove from history

**Platform setup:**
- Vercel: Dashboard → Project → Settings → Environment Variables. Set per-environment (Production / Preview / Development).
- Railway: Project → Service → Variables. Use Railway's "Reference Variables" to share across services.
- Fly.io: `fly secrets set KEY=value` — never in `fly.toml`.
- Docker: pass via `--env-file .env.production` or secrets mount — never bake into the image.

---

## Phase 2 — Platform-Specific Setup

### Vercel (frontend / Next.js)

```bash
npm i -g vercel
vercel login
vercel --prod   # first deploy; follow prompts to link project
```

**Settings to configure:**
- Build command: confirm it matches `package.json scripts.build`
- Output directory: `dist`, `.next`, `out` — depends on framework
- Node.js version: pin in `package.json` → `"engines": { "node": "20.x" }`
- Domain: Settings → Domains → add custom domain + configure DNS

**Preview deploys:**
- Every PR branch gets a unique preview URL automatically — no config needed
- Use preview deploys to test before merging

---

### Railway (backend / fullstack)

```bash
npm i -g @railway/cli
railway login
railway init      # in project root
railway up        # deploy
```

**Settings to configure:**
- Start command: Railway auto-detects from `package.json scripts.start` — verify it's correct
- Health check path: Settings → Deploy → Health Check Path → set to `/health`
- Restart policy: On failure, max 3 restarts (prevents crash loops burning credits)
- Postgres: Add Plugin → PostgreSQL — Railway injects `DATABASE_URL` automatically

---

### Fly.io (containers / persistent workloads)

```bash
brew install flyctl
fly auth login
fly launch        # generates fly.toml
fly deploy
```

**`fly.toml` essentials:**
```toml
[http_service]
  internal_port = 3000   # match your app's PORT
  force_https = true

[[vm]]
  size = "shared-cpu-1x"  # start here; scale up if needed

[checks]
  [checks.health]
    type = "http"
    path = "/health"
    interval = "30s"
    timeout = "5s"
```

**Persistent volumes (if needed):**
```bash
fly volumes create data --size 1  # 1GB
```
Mount in `fly.toml` under `[mounts]`.

---

### Docker

**Dockerfile (Node.js example — production-ready):**
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
USER node
CMD ["node", "src/index.js"]
```

**Rules:**
- Use multi-stage builds — don't ship dev dependencies or build tools
- Pin the Node/Python version — `node:20-alpine`, not `node:latest`
- Run as non-root user (`USER node`) — don't run as root in production
- `.dockerignore` must include: `node_modules`, `.env`, `.git`, `*.log`

**Docker Compose (local dev + staging):**
```yaml
services:
  app:
    build: .
    ports: ["3000:3000"]
    env_file: .env
    depends_on: [db]
  db:
    image: postgres:16-alpine
    volumes: [pgdata:/var/lib/postgresql/data]
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
volumes:
  pgdata:
```

---

## Phase 3 — CI/CD Pipeline

**GitHub Actions — standard deploy workflow:**

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci
      - run: npm test       # fail fast if tests break
      - run: npm run build  # fail fast if build breaks

      # Platform-specific deploy step:
      # Vercel: use vercel/action
      # Railway: use railwayapp/railway-action
      # Fly: use superfly/flyctl-actions
```

**Rules:**
- Tests run before deploy — a failing test blocks the deploy
- Build runs before deploy — a broken build blocks the deploy
- Use secrets for deploy tokens: `Settings → Secrets → Actions` in GitHub
- Never put deploy credentials in the workflow file

---

## Phase 4 — Health Checks & Rollback

**Health check endpoint (required):**

Every deployed service must expose:
```
GET /health
Response: 200 OK
Body: { "status": "ok", "timestamp": "..." }
```

This is the endpoint your platform pings to decide if the deploy succeeded. If it returns non-200, the platform rolls back automatically.

**Rollback procedure:**
- **Vercel**: Deployments tab → find last good deploy → "Promote to Production"
- **Railway**: Deployments → click previous deploy → "Redeploy"
- **Fly.io**: `fly releases list` → `fly deploy --image [previous-image]`
- **Docker**: `docker service update --rollback app`

**Keep rollback < 5 minutes.** If it takes longer, something in the pipeline is wrong.

---

## Phase 5 — Pre-Launch Checklist

Run through this before declaring a deployment production-ready:

- [ ] Health check endpoint responds with 200
- [ ] All environment variables are set in the production environment
- [ ] DB migrations have run (or will run on startup)
- [ ] HTTPS is enforced — HTTP redirects to HTTPS
- [ ] Error monitoring is wired up (Sentry, or see `/monitor`)
- [ ] A test deploy was done before the real one — preview/staging environment
- [ ] Rollback has been tested — verify you can actually roll back, don't assume
- [ ] Deploy notification is set up (Slack or email on deploy success/failure)

---

## Rules

- **Every secret goes into the platform's secret store** — not in the repo, not in the Dockerfile, not in the workflow file.
- **Health checks are non-negotiable.** If the platform can't verify a successful deploy, it can't roll back a bad one.
- **Pin versions.** Node version, Docker base image, GitHub Actions versions. Floating tags (`latest`) break at the worst time.
- **Staging before production.** If the platform supports preview/staging environments, use them. Don't test in production.
- **Automate the deploy, not the decision.** CI deploys automatically on `main`, but a human decides when to merge.
