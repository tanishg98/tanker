# FAQ

## Is Tanker an alternative to MetaGPT / AutoGen / CrewAI?

Cousins, not alternatives. They're general-purpose multi-agent frameworks. Tanker is opinionated, Claude Code-native, and ends in a deployed product (not just code). Detailed comparison: [Tanker vs MetaGPT](./comparisons/metagpt.md).

## Does Tanker work without Claude Code?

No. Tanker's primitives — slash commands, agent dispatch, the always-on rules system — are Claude Code features. Tanker is a `.claude/` folder you drop into a project Claude Code opens.

## Do I need Anthropic credits?

Yes — Tanker uses Claude (Opus + Sonnet) via Claude Code. A typical `/cto` run costs $3–6. Default cost cap is $10 per run.

## Can I use a different LLM?

Today, no — Tanker is Claude Code-native. Multi-provider support is on the roadmap (steal #10 from MetaGPT).

## Is the data shared with anyone?

No. Brain index runs locally with a default ChromaDB embedder. Vault credentials live in `~/.claude/vault/credentials.json` (0600). Nothing is sent to a Tanker-controlled server. Anthropic's API does see the LLM prompts.

## How do I add a new skill?

1. Create `.claude/skills/<name>/SKILL.md` with YAML frontmatter (name, description, triggers, args).
2. Write the prompt body using the SOP triplet pattern (Constraints / Reference / Output Format).
3. Wire into the chain — what comes before (input), what comes after (handoff).

See `/grill` SKILL.md as a template.

## How do I add a new agent?

1. Create `.claude/agents/<name>.md` with YAML frontmatter (name, description, tools, model).
2. Decide read-only vs scoped-write — don't give file write tools to a review agent.
3. Output structured JSON when the agent's output feeds into another skill (use `.claude/schemas/review.schema.json` as template).

## Can I use Tanker on an existing project?

Yes. Run `bash install.sh` in the project root. The installer detects existing `.claude/` and backs it up. Use `/explore` + `/grill` + `/createplan` flow for adding features to an existing codebase.

## Why two human gates?

Because the alternative — fully autonomous shipping — produces slop, and the other alternative — pause everywhere — wastes attention. Two gates at the highest-leverage decisions (PRD, MVP) compound human judgment without burning attention. See [Human gates](./architecture/gates.md).

## How do I contribute?

PRs welcome. Bar:
- New skills: SOP triplet pattern, JSON sidecar schema, worked example.
- New agents: structured JSON output validated against a schema.
- New rules: argued in the PR description with concrete examples of the failure mode it prevents.

## Can I run Tanker against private codebases?

Yes — Tanker doesn't send your code anywhere except Anthropic (via the LLM API). Same threat model as Claude Code itself.

## Is there a hosted version?

Not yet. `tanker.dev` (planned) will host a one-click `/cto` for trial. For now, Tanker runs locally.
