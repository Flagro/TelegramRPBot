from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Protocol


@dataclass
class AgentInput:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryState:
    scope_key: Optional[str] = None
    provider_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentTool:
    name: str
    description: str
    handler: Callable[..., Any]


@dataclass
class AgentStreamChunk:
    text_chunk: Optional[str] = None
    total_text: Optional[str] = None
    provider_metadata: Dict[str, Any] = field(default_factory=dict)


class AgentRuntime(Protocol):
    async def stream(
        self,
        instructions: str,
        input: AgentInput,
        tools: List[AgentTool],
        memory_state: Optional[MemoryState] = None,
    ) -> AsyncIterator[AgentStreamChunk]:
        ...
