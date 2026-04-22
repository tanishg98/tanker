# Salary Range Estimator (India) — Implementation Plan

**Status:** `100% complete` — all steps done. Local smoke test passed.

---

## What we're building

A public web tool where a user pastes a LinkedIn profile URL. The system fetches their current role, company, YOE, and previous experience, then fans out to scrape job portals (Naukri, LinkedIn Jobs, Indeed India), salary pages (Glassdoor India, Ambitionbox, Levels.fyi), and Reddit threads in real-time. Results are stored and used to return a CTC range (low / mid / high). A feedback prompt ("in range / slightly off / way off") crowdsources accuracy signals that improve source weighting over time.

---

## Out of Scope (v1)

- Equity / ESOP calculation
- Non-India geographies
- Authentication or user accounts
- Browser extension (V2)
- Feedback loop processing / source reweighting (V2 — data collection only in v1)
- Resume parsing (PDF, DOCX)

---

## Key Decisions

| Decision | Chosen | Rejected | Reason |
|----------|--------|----------|--------|
| LinkedIn profile extraction | `httpx` plain HTTP scrape + Playwright fallback | Proxycurl API | Proxycurl costs money; httpx covers public profiles; Playwright as last resort |
| Scraping model | On-demand per query, results cached 7 days by role+city+yoe bucket | Nightly batch cron | On-demand means data is always query-relevant; caching prevents re-scraping |
| Async UX | Return `job_id` immediately, poll every 2s | Make user wait 15s | Scraping takes 10–20s; async with live progress steps is the right UX |
| Salary extraction | Regex patterns (`₹?\d+(?:\.\d+)?\s*(?:L\|LPA\|lakhs?)`) + structured HTML fields | LLM extraction | Regex handles 90% of cases; faster, free, deterministic |
| LLM role | Groq API + Gemma 2 9B — title normalization only, fallback when regex fails | Claude Haiku | Groq free tier (14,400 req/day), Gemma 2 9B sufficient for title normalization |
| LLM model | `gemma2-9b-it` via Groq | Claude Haiku, Gemini Flash | Free, no credit card, fast enough (~500ms) |
| Range synthesis | Pure statistics — median, p25, p75 weighted by sample size | LLM synthesis | Data pipeline produces numbers; no LLM needed to average them |
| Storage | SQLite — two tables: `salary_data_points` + `feedback` | PostgreSQL | Zero infra cost, no concurrent write pressure at this scale |
| Frontend | Single HTML file, vanilla JS, async polling | React / Next.js | Single-input tool; framework overhead not justified |
| Hosting | Single FastAPI process on Fly.io (persistent volume for SQLite) | Serverless | Always-on process needed for scraping jobs; SQLite needs persistent disk |

---

## Steps

### 🟩 Step 1: Project Structure + SQLite Schema

**Goal:** Establish project layout and the database schema that everything else writes to and reads from.

**Files touched:**
- `salary-estimator/db/schema.sql`
- `salary-estimator/db/init_db.py`
- `salary-estimator/requirements.txt`
- `salary-estimator/.env.example`
- `salary-estimator/.gitignore`

**Subtasks:**
- 🟥 Create project directory at `/Users/tanishgirotra1/projects/salary-estimator/`
- 🟥 Define `salary_data_points` table (id, source, raw_title, normalized_title, location, yoe_min, yoe_max, salary_low, salary_mid, salary_high, sample_size, source_date, created_at)
- 🟥 Define `scrape_jobs` table (id, cache_key, status, profile_json, result_json, created_at, completed_at)
- 🟥 Define `feedback` table (id, job_id, signal [in_range/slightly_off/way_off], actual_ctc, created_at)
- 🟥 Write `init_db.py` — runs schema.sql against `salary.db`
- 🟥 Write `requirements.txt` with all deps
- 🟥 Write `.env.example` with `GROQ_API_KEY`, `DB_PATH`

---

### 🟩 Step 2: Scraping Pipeline — Profile + Salary Sources

**Goal:** Given a LinkedIn URL, extract profile data and fan out to 5+ sources to collect salary signals, store raw results in SQLite.

**Files touched:**
- `salary-estimator/scraper/linkedin.py`
- `salary-estimator/scraper/naukri.py`
- `salary-estimator/scraper/ambitionbox.py`
- `salary-estimator/scraper/glassdoor.py`
- `salary-estimator/scraper/levels_fyi.py`
- `salary-estimator/scraper/reddit.py`
- `salary-estimator/scraper/salary_extract.py` (shared regex extraction)
- `salary-estimator/scraper/pipeline.py` (orchestrator)

**Subtasks:**
- 🟥 Write `salary_extract.py`: regex extractor for Indian salary patterns (`₹?\d+(?:\.\d+)?\s*(?:L|LPA|lakh|lakhs|k)`) — normalise everything to annual CTC in lakhs
- 🟥 Write `linkedin.py`: httpx GET public profile → parse title, company, location from `<title>` and og tags; return `ProfileData` dict. On login-wall response → return `None` (caller handles fallback)
- 🟥 Write `naukri.py`: search `naukri.com` jobs for `{title} {city}`, extract salary from job listings (structured `salary` field in HTML/JSON)
- 🟥 Write `ambitionbox.py`: scrape Ambitionbox salary pages for role + city combinations
- 🟥 Write `glassdoor.py`: scrape Glassdoor India salary pages for role + city
- 🟥 Write `levels_fyi.py`: hit Levels.fyi India JSON endpoint, extract by role
- 🟥 Write `reddit.py`: Reddit public JSON API (`reddit.com/r/cscareerquestionsIndia+india+developersIndia/search.json?q={title}+salary+{city}&sort=relevance`) — extract salary mentions from post titles + bodies
- 🟥 Write `pipeline.py`: given `ProfileData`, run all scrapers concurrently (`asyncio.gather`), collect `SalaryDataPoint` list, upsert to SQLite, return aggregated range. Cache by `hash(normalized_title + city + yoe_bucket)`, TTL 7 days

---

### 🟩 Step 3: FastAPI Backend — Job Queue + API

**Goal:** API that accepts a LinkedIn URL, kicks off an async scrape job, and returns results via polling. Includes Groq/Gemma title normalization and feedback endpoint.

**Files touched:**
- `salary-estimator/api/main.py`
- `salary-estimator/api/models.py`
- `salary-estimator/api/title_normalizer.py`
- `salary-estimator/api/salary_lookup.py`
- `salary-estimator/api/jobs.py`

**Subtasks:**
- 🟥 Define Pydantic models: `EstimateRequest`, `ProfileData`, `SalaryRange`, `EstimateResponse`, `JobStatus`, `FeedbackRequest`
- 🟥 Write `title_normalizer.py`: Groq API call with `gemma2-9b-it` — input raw title → output canonical title (e.g. "SDE 2" → "Software Engineer"). Only called when regex lookup table misses. Include lookup table for top 50 Indian job titles as first pass (no API call needed)
- 🟥 Write `salary_lookup.py`: query SQLite for matching data points, compute weighted p25/p50/p75 across sources, return `SalaryRange`
- 🟥 Write `jobs.py`: in-memory job store (dict) + background task runner using FastAPI `BackgroundTasks`. `create_job()` → returns `job_id`, runs pipeline in background. `get_job(job_id)` → returns status + result
- 🟥 Wire endpoints:
  - `POST /api/estimate` → create job, return `{job_id, status: "scraping"}`
  - `GET /api/estimate/{job_id}` → return job status + result when done
  - `POST /api/feedback` → store signal against job_id
  - `GET /api/health` → DB row count, job queue size
- 🟥 IP rate limiting: simple in-memory counter, max 10 requests/hour per IP

---

### 🟩 Step 4: Frontend — Async Poll UI

**Goal:** Single HTML page: LinkedIn URL input → live progress steps → salary range card → feedback prompt.

**Files touched:**
- `salary-estimator/frontend/index.html`

**Subtasks:**
- 🟥 URL input form — single field, submit button
- 🟥 Progress steps display: "Fetching profile → Scanning job portals → Checking Glassdoor → Reading Reddit → Synthesizing range" — each ticks green as it completes (poll `/api/estimate/{job_id}` every 2s, backend sets progress flags in job store)
- 🟥 Results card: horizontal range bar (low / mid / high in ₹L), data points count, sources list badge
- 🟥 Feedback row below result: "How accurate is this?" [In range] [Slightly off] [Way off] — calls `POST /api/feedback`, shows thank-you on submit
- 🟥 Error states: LinkedIn blocked (show manual form fallback), no data found, rate limited
- 🟥 Mobile-first, 375px minimum width
- 🟥 `prefers-reduced-motion` respected on progress animations
- 🟥 No AI slop patterns (no purple gradients, no icon-grid, no centered hero copy)

---

### 🟩 Step 5: Deployment Config

**Goal:** App runs on Fly.io with persistent SQLite volume; accessible at a public URL.

**Files touched:**
- `salary-estimator/fly.toml`
- `salary-estimator/Dockerfile`
- `salary-estimator/README.md`

**Subtasks:**
- 🟥 Write `Dockerfile`: Python 3.12 slim, install Playwright chromium (for Ambitionbox fallback), copy app, run `uvicorn api.main:app`
- 🟥 Write `fly.toml`: single machine, persistent volume mounted at `/data` (SQLite lives there), set `DB_PATH=/data/salary.db`
- 🟥 Serve `frontend/index.html` via FastAPI `StaticFiles` mount at `/`
- 🟥 Write `README.md`: env vars, how to run locally, how to deploy

---

## Risks & Watch-outs

- **LinkedIn httpx returns login wall for most profiles** — expected. Fall back immediately to manual form (role + YOE + city). Manual form is just as fast and doesn't depend on scraping.
- **Ambitionbox / Glassdoor block scrapers** — each scraper is independently failable. Pipeline logs the failure and continues with remaining sources. If a scraper returns 0 results it's dropped silently; the range is computed from whatever sources responded.
- **Reddit API rate limits** — Reddit's public JSON API allows ~60 req/min unauthenticated. With 7-day caching this is fine. If blocked, Reddit is dropped as a source for that query.
- **Sparse data for non-tech roles** — return `confidence: "low"` and wider range when `sample_size < 15`. Never suppress the result.
- **Groq free tier limits** — 14,400 req/day for Gemma 2 9B. Title normalization only fires on cache miss (~20% of queries). At 1,000 queries/day that's 200 Groq calls. Well within limits.
- **In-memory job store resets on restart** — acceptable for v1. Pending jobs are lost on deploy. Users just re-submit.
