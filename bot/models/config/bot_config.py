from typing import Literal, Optional

from pydantic import Field
from .base_config import BaseYAMLConfigModel


class MemoryConfig(BaseYAMLConfigModel):
    enabled: bool = False
    strategy: Literal[
        "legacy_prompt",
        "expanded_prompt",
        "agent_tools_shadow",
        "agent_tools",
        "hybrid_provider_state",
    ] = "legacy_prompt"
    runtime: Literal["omnimodkit", "openai_agents_sdk"] = "omnimodkit"
    facts_access: Literal["prompt", "tools"] = "prompt"
    provider_state: Literal[
        "disabled", "responses_previous_id", "openai_conversation"
    ] = "disabled"
    provider_state_ttl_hours: int = 24
    fallback_last_n_messages: int = 6
    summary_enabled: bool = False
    summary_token_target: int = 800
    shadow_mode: bool = False
    agent_model: Optional[str] = None


class BotConfig(BaseYAMLConfigModel):
    default_language: str
    last_n_messages_to_remember: int
    last_n_messages_to_store: Optional[int] = None
    default_usage_limit: int
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
