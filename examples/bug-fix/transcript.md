# Bug fix — `/explore → /debug → /test-gen → /ship` transcript

> **Status: PLACEHOLDER.** Fill in real run.

## Steps

1. `/explore` mapped the revenue dashboard data path: `apps/web/lib/revenue.ts` → `apps/api/routes/revenue.py` → `select sum(...) from orders where created_at::date = current_date`.
2. `/debug` traced symptom: `current_date` resolves to UTC; merchant in IST sees yesterday's data after 18:30 IST.
3. Fix: pass `merchant_timezone` from session, use `current_date at time zone $tz`.
4. `/test-gen` wrote three tests: IST 06:00, IST 18:00, IST 23:55. All pass with fix.
5. `/ship` opened PR with fix + tests.

## Honest debrief

- [TBD]
