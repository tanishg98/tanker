# tanker.yaml — model + provider configuration

Tanker reads `.claude/tanker.yaml` for per-skill / per-agent model preferences, retry caps, and cost ceilings. Override per-project with `.claude/tanker.local.yaml`.

## Why config-driven model selection

Without per-skill model preferences, every skill defaults to the same model. That's wasteful — `/reflect` doesn't need Opus, but `/prd` does. With `tanker.yaml`:

- **Hard reasoning** (`/grill`, `/prd`, `/architect`, `/advisor`) → Opus
- **Workhorse** (`/execute`, `/backend-builder`, `/ship`, `/deploy`) → Sonnet
- **Cheap/repetitive** (`/reflect`, `/context-save`, `/learn`) → Haiku

Cuts run cost by ~40-60% on a typical `/cto` without measurable quality loss on the bottleneck steps.

## Schema

See [`.claude/tanker.yaml`](https://github.com/tanishg98/tanker/blob/main/.claude/tanker.yaml) for the canonical reference. Key sections:

| Section | Purpose |
|---|---|
| `default_model` | Fallback model when no per-skill override |
| `models` | Per-skill model preferences (`/skill-name: model-id`) |
| `agents` | Per-agent model preferences |
| `providers` | Anthropic (default) + OpenAI / Azure stubs for future multi-LLM |
| `advisor.pairs` | Cross-model peer review pairings (author + reviewer) |
| `cost_ceilings` | Default `--max-cost-usd` per run type |
| `retries` | Bounded retry caps (steal #4) |

## How it's read

The `/cto` orchestrator and individual skills consult `tanker.yaml` via a tiny helper:

```bash
python3 -c "
import yaml, sys
cfg = yaml.safe_load(open('.claude/tanker.yaml'))
local_path = '.claude/tanker.local.yaml'
import os
if os.path.exists(local_path):
    cfg.update(yaml.safe_load(open(local_path)))
skill = sys.argv[1]
print(cfg['models'].get(skill, cfg['default_model']))
"  /prd
# → claude-opus-4-7
```

Skills that respect the config pass the resolved model id when dispatching subagents.

## Multi-LLM (future)

Today Tanker is Claude Code-native — the LLM provider is fixed by the Claude Code session. The `providers` section in `tanker.yaml` is a forward-compatible stub. When Tanker grows multi-LLM support, the model resolver will:

1. Look up the model id (e.g. `claude-opus-4-7` vs `gpt-4-turbo`).
2. Find the provider section by family (`claude-*` → `anthropic`, `gpt-*` → `openai`).
3. Read the API key from `~/.claude/vault/credentials.json`.
4. Dispatch via the appropriate SDK.

Until then, only `claude-*` models work, and they're routed through Claude Code itself.

## Project overrides

For project-specific overrides (e.g. a budget-sensitive project that wants Sonnet everywhere), drop a `.claude/tanker.local.yaml` in the consuming project root:

```yaml
# .claude/tanker.local.yaml
default_model: claude-sonnet-4-6  # never use Opus on this project
cost_ceilings:
  cto_default_usd: 5.00            # half the default
```

`tanker.local.yaml` is a shallow override on top of `tanker.yaml`. It's gitignored by default.
