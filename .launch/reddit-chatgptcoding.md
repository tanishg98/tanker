# r/ChatGPTCoding post

## Title

```
Tanker: turned my Claude Code workflow into a framework that ships deployed products from a brief (open source)
```

## Body

```
Most "AI builds your product" tools either:
1. Generate code on disk and stop, or
2. Go fully autonomous and ship slop

Tanker tries a third path: pre-qualified human gates. Two of them — one at the PRD, one at the local MVP. A review agent has to PASS first; you only see the gate when there's something worth reviewing.

End-to-end: `/cto "<brief>"` → ~3 hours later, you have a live deployed URL. Total time you spend reviewing: ~30 min.

What it provisions (real APIs, not mocked):
- GitHub repo + branch protection + secrets
- Supabase project + RLS migrations
- Vercel project + env vars + preview deploys
- Railway service + healthcheck

Costs ~$3-6 per run with default settings. Cost ceiling at $10 (raise with --max-cost-usd).

The pieces I borrowed from MetaGPT:
- Typed Message envelope (provenance, replay)
- SOP triplet prompt pattern
- Bounded review-retry loop
- DataInterpreter → my /analyst skill

The pieces that are different:
- Real provisioning + deploy + monitoring (not just code)
- Resumability via state.json checkpointing
- Local semantic retrieval over your knowledge corpus
- Opinionated quality rails (always-on rules)

Open source, MIT.

Repo: https://github.com/tanishg98/tanker
Comparisons: https://tanker.dev/comparisons/

What's the most useful question you'd ask before adopting something like this?
```

## Don't

- Don't open with "I built X" — skip the framing, lead with the move.
- Reply quickly to mod questions about self-promotion. Have the karma to back it up.
