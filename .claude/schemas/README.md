# Tanker JSON Schemas

These schemas validate the JSON sidecars that skills and agents produce. They make Tanker outputs machine-readable, which means:

- Reviewer agents (prd-reviewer, pre-merge, mvp-reviewer) can read structured JSON instead of re-parsing markdown.
- The `/cto` orchestrator's retry loop can decide based on `verdict` + `findings[].fix_kind` instead of regexing prose.
- External tooling (CI, dashboards, audits) can consume Tanker outputs directly.

## Files

| Schema | Validates | Produced by |
|---|---|---|
| `prd.schema.json` | `outputs/<slug>/prd/prd.json` | `/prd` |
| `architecture.schema.json` | `outputs/<slug>/architecture.json` | `/architect` |
| `plan.schema.json` | `outputs/<slug>/plan.json` | `/createplan` |
| `review.schema.json` | `outputs/<slug>/reviews/*.json` | `pre-merge`, `prd-reviewer`, `mvp-reviewer`, `/autoresearch-review` |
| `message.schema.json` | one line in `outputs/<slug>/messages.jsonl` | every skill + agent that runs under `/cto` |

## Validation

If you have `ajv-cli` installed:

```bash
npx ajv-cli validate -s .claude/schemas/prd.schema.json -d outputs/<slug>/prd/prd.json
```

Or `python -m jsonschema`:

```bash
python -m jsonschema -i outputs/<slug>/prd/prd.json .claude/schemas/prd.schema.json
```

## Convention

- All schemas use 2020-12 Draft.
- All `id` fields use a typed prefix (`FT-`, `S-`, `FL-`, `C-`, `API-`, `TD-`, `R-`, `D-`, `P-`, `F-`) so cross-references between artifacts are unambiguous.
- All `*_questions` and `*_decisions` arrays must be empty in finalized output. If you have unresolved questions, surface them BEFORE producing the artifact, not inside it.
