from dataclasses import dataclass, field
from typing import List, Optional

from ..models.config.bot_config import MemoryConfig
from ..models.handlers_input import Context, Person, TranscribedMessage
from .db import DB
from .memory_utils import build_scope_key, get_display_name, get_participant_key
from .prompt_manager import PromptManager


@dataclass
class MemoryToolResult:
    tool_name: str
    result_count: int
    details: List[str] = field(default_factory=list)


@dataclass
class PreparedMemoryContext:
    user_input: str
    scope_key: Optional[str] = None
    shadow_tool_results: List[MemoryToolResult] = field(default_factory=list)


class MemoryTools:
    def __init__(self, db: DB) -> None:
        self.db = db

    async def get_user_facts(self, context: Context, person: Person) -> List[str]:
        facts = await self.db.user_facts.get_user_facts_by_participant(
            context=context,
            participant_key=get_participant_key(person),
            fallback_user_handle=person.user_handle,
        )
        return facts

    async def get_replied_user_facts(self, context: Context) -> List[str]:
        if not context.replied_to_user_handle:
            return []
        return await self.db.user_facts.get_facts_for_user_handle(
            context=context,
            user_handle=context.replied_to_user_handle,
        )

    async def search_chat_facts(
        self,
        context: Context,
        query: Optional[str] = None,
        participant_key: Optional[str] = None,
    ) -> List[str]:
        return await self.db.user_facts.search_chat_facts(
            context=context,
            query=query,
            participant_key=participant_key,
        )

    async def search_recent_dialog(
        self,
        context: Context,
        query: Optional[str] = None,
        participant_key: Optional[str] = None,
        limit: int = 6,
    ) -> List[str]:
        return await self.db.dialogs.search_recent_dialog(
            context=context,
            query=query,
            participant_key=participant_key,
            limit=limit,
        )


class MemoryManager:
    def __init__(
        self,
        db: DB,
        prompt_manager: PromptManager,
        memory_config: MemoryConfig,
    ) -> None:
        self.db = db
        self.prompt_manager = prompt_manager
        self.memory_config = memory_config
        self.tools = MemoryTools(db)

    def is_legacy_mode(self) -> bool:
        return (
            not self.memory_config.enabled
            or self.memory_config.strategy == "legacy_prompt"
        )

    async def get_scope_key(self, context: Context) -> str:
        chat_mode = await self.db.chat_modes.get_chat_mode(context)
        return build_scope_key(context=context, mode_id=chat_mode.mode_name)

    async def prepare_context(
        self,
        initiator: Person,
        context: Context,
        user_transcribed_message: TranscribedMessage,
    ) -> PreparedMemoryContext:
        if self.is_legacy_mode():
            user_input = await self.prompt_manager.compose_prompt(
                initiator=initiator,
                context=context,
                user_transcribed_message=user_transcribed_message,
            )
            return PreparedMemoryContext(user_input=user_input)

        scope_key = await self.get_scope_key(context)
        if self.memory_config.strategy == "expanded_prompt":
            user_input = await self._compose_expanded_prompt(
                initiator=initiator,
                context=context,
                user_transcribed_message=user_transcribed_message,
            )
            return PreparedMemoryContext(user_input=user_input, scope_key=scope_key)

        user_input = await self.prompt_manager.compose_prompt(
            initiator=initiator,
            context=context,
            user_transcribed_message=user_transcribed_message,
        )
        shadow_results = []
        if self.memory_config.strategy == "agent_tools_shadow":
            shadow_results = await self.run_shadow_tools(initiator, context)
        return PreparedMemoryContext(
            user_input=user_input,
            scope_key=scope_key,
            shadow_tool_results=shadow_results,
        )

    async def _compose_expanded_prompt(
        self,
        initiator: Person,
        context: Context,
        user_transcribed_message: TranscribedMessage,
    ) -> str:
        legacy_prompt = await self.prompt_manager.compose_prompt(
            initiator=initiator,
            context=context,
            user_transcribed_message=user_transcribed_message,
        )
        identity_prompt = "\n".join(
            [
                "Current participant identity:",
                f"participant_key: {get_participant_key(initiator)}",
                f"display_name: {get_display_name(initiator)}",
                f"telegram_id: {initiator.telegram_id}",
            ]
        )
        return "\n\n".join([identity_prompt, legacy_prompt])

    async def run_shadow_tools(
        self, initiator: Person, context: Context
    ) -> List[MemoryToolResult]:
        user_facts = await self.tools.get_user_facts(context, initiator)
        replied_user_facts = await self.tools.get_replied_user_facts(context)
        recent_dialog = await self.tools.search_recent_dialog(
            context=context,
            participant_key=get_participant_key(initiator),
            limit=self.memory_config.fallback_last_n_messages,
        )
        return [
            MemoryToolResult("get_user_facts", len(user_facts), user_facts[:3]),
            MemoryToolResult(
                "get_replied_user_facts",
                len(replied_user_facts),
                replied_user_facts[:3],
            ),
            MemoryToolResult(
                "search_recent_dialog",
                len(recent_dialog),
                recent_dialog[:3],
            ),
        ]
