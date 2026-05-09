"""Base agent — handles the Claude tool-use loop for all specialists."""
from __future__ import annotations

import json
from typing import Any

import anthropic

from ..tools.whoop_tools import TOOL_DEFINITIONS, WhoopToolExecutor

DEFAULT_MODEL = "claude-opus-4-7"
MAX_TOKENS = 4096


class BaseAgent:
    """
    Base class for all specialist agents. Subclasses set their system prompt.
    Runs a full agentic loop: Claude calls WHOOP tools, gets results, produces final answer.
    """

    system_prompt: str = ""
    name: str = "Agent"

    def __init__(self, executor: WhoopToolExecutor, model: str = DEFAULT_MODEL):
        self._executor = executor
        self._model = model
        self._client = anthropic.Anthropic()

    def run(self, user_message: str, context: str = "") -> str:
        """Run the agent on a question and return the final text response."""
        messages: list[dict[str, Any]] = []

        if context:
            messages.append({"role": "user", "content": f"Context from other specialists:\n{context}"})
            messages.append({"role": "assistant", "content": "Understood. I have the context from other specialists."})

        messages.append({"role": "user", "content": user_message})

        while True:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=MAX_TOKENS,
                system=self.system_prompt,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

            # Collect any text blocks first
            text_parts = [b.text for b in response.content if b.type == "text"]

            if response.stop_reason == "end_turn":
                return "\n".join(text_parts).strip()

            if response.stop_reason != "tool_use":
                return "\n".join(text_parts).strip()

            # Execute all tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = self._executor.execute(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Append assistant turn + tool results and loop
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

    def brief(self) -> str:
        """Generate today's specialist brief. Subclasses can override the prompt."""
        return self.run(
            "Pull all relevant WHOOP data and provide your specialist assessment for today. "
            "Be specific, data-driven, and actionable."
        )
