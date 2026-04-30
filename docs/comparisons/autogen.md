# Tanker vs AutoGen

[Microsoft AutoGen](https://github.com/microsoft/autogen) is a multi-agent conversation framework. Agents talk to each other and to humans, with code execution and tool use mixed in.

## TL;DR

- **AutoGen is a conversation framework.** Tanker is a product-build pipeline.
- **AutoGen ships agents.** Tanker ships products.

If you want to build a custom multi-agent application, use AutoGen. If you want to ship a deployed product from a one-line brief, use Tanker.

## Side-by-side

| | AutoGen | Tanker |
|---|---|---|
| **Primary abstraction** | `ConversableAgent` + group chat | Skill + Agent + Rule |
| **Programming model** | Python API | Claude Code slash commands |
| **Agent communication** | Conversational message-passing | Typed Message envelope (`messages.jsonl`) + state.json |
| **Code execution** | Built-in `LocalCommandLineCodeExecutor` | Bash tool (Claude Code) |
| **Human input** | `human_input_mode` enum | Two mandatory review gates |
| **Multi-LLM** | Yes — OpenAI, Azure, local, etc. | Claude Code-native |
| **Deployment** | You wire it | Built-in via provisioner agents |
| **Use case** | Custom agentic apps | Product builds |

## What Tanker borrows from AutoGen

- **Group chat → typed Message envelope.** AutoGen's group chat with structured handoffs informed Tanker's `messages.jsonl` design.
- **Human-in-the-loop modes.** AutoGen's `ALWAYS / TERMINATE / NEVER` for human input is conceptually close to Tanker's `gated / --full-auto` modes.

## What's different

- **Scope.** AutoGen is a kit; Tanker is a product.
- **Output.** AutoGen returns conversation transcripts. Tanker returns deployed URLs.
- **Quality rails.** Tanker has always-on rules. AutoGen leaves quality to your prompts.

## When to use which

**AutoGen if** you're building a custom agent application — research workflow, synthetic data generation, conversation-heavy automation.

**Tanker if** you want to ship products faster, on Claude Code, with provisioning + deploy + monitoring built in.
