from typing import AsyncIterator, List, Optional

from .agent_runtime import AgentInput, AgentStreamChunk, AgentTool, MemoryState


class OpenAIAgentsRuntime:
    def __init__(
        self,
        model: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ) -> None:
        self.model = model or "gpt-4o"
        self.openai_api_key = openai_api_key

    async def stream(
        self,
        instructions: str,
        input: AgentInput,
        tools: List[AgentTool],
        memory_state: Optional[MemoryState] = None,
    ) -> AsyncIterator[AgentStreamChunk]:
        try:
            from agents import Agent, OpenAIProvider, RunConfig, Runner, function_tool
            from openai.types.responses import ResponseTextDeltaEvent
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI Agents runtime requires the optional 'openai-agents' "
                "dependency. Install project dependencies before enabling "
                "memory.runtime='openai_agents_sdk'."
            ) from exc

        sdk_tools = []
        for tool in tools:
            sdk_tools.append(
                function_tool(
                    name_override=tool.name,
                    description_override=tool.description,
                )(tool.handler)
            )

        agent = Agent(
            name="Telegram RP Reply Agent",
            model=self.model,
            instructions=instructions,
            tools=sdk_tools,
        )

        run_config = None
        if self.openai_api_key:
            run_config = RunConfig(
                model_provider=OpenAIProvider(api_key=self.openai_api_key)
            )

        if run_config:
            result = Runner.run_streamed(agent, input=input.text, run_config=run_config)
        else:
            result = Runner.run_streamed(agent, input=input.text)
        total_text = ""
        async for event in result.stream_events():
            if event.type != "raw_response_event":
                continue
            if isinstance(event.data, ResponseTextDeltaEvent):
                total_text += event.data.delta
                yield AgentStreamChunk(
                    text_chunk=event.data.delta,
                    total_text=total_text,
                    provider_metadata=self._provider_metadata(memory_state),
                )

        final_output = getattr(result, "final_output", None)
        if final_output and str(final_output) != total_text:
            final_text = str(final_output)
            if final_text.startswith(total_text):
                final_delta = final_text[len(total_text) :]
                if final_delta:
                    yield AgentStreamChunk(
                        text_chunk=final_delta,
                        total_text=final_text,
                        provider_metadata=self._provider_metadata(memory_state),
                    )
            total_text = final_text

    def _provider_metadata(
        self, memory_state: Optional[MemoryState]
    ) -> dict:
        provider_metadata = {
            "provider": "openai",
            "runtime": "openai_agents_sdk",
            "model": self.model,
        }
        if memory_state and memory_state.scope_key:
            provider_metadata["scope_key"] = memory_state.scope_key
        return provider_metadata
