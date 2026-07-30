from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Tuple, Union, Literal

from bson import ObjectId
from pydantic import BaseModel, ConfigDict

from ..models.handlers_input import Context, Person, TranscribedMessage


class ChatModeRecord(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: ObjectId
    mode_name: str
    mode_description: str


class UserUsageRecord(BaseModel):
    this_month_usage: int
    limit: int
    last_reset: datetime


class BaseStore(Protocol):
    async def create_if_not_exists(self, context: Context, person: Person) -> None:
        pass

    async def update_if_needed(self, person: Person, context: Context) -> None:
        pass

    async def clear_user_data(self, user_handle: str) -> None:
        pass


class UsersStore(BaseStore, Protocol):
    async def get_person_by_handle(self, user_handle: str) -> Person:
        pass

    async def ban_user(self, user_handle: str, time_seconds: int) -> None:
        pass

    async def unban_user(self, user_handle: str) -> None:
        pass

    async def is_user_banned(self, user_handle: str) -> bool:
        pass

    async def has_accepted_terms(self, user_handle: str) -> bool:
        pass

    async def has_declined_terms(self, user_handle: str) -> bool:
        pass

    async def accept_terms(self, user_handle: str) -> None:
        pass

    async def decline_terms(self, user_handle: str) -> None:
        pass


class UserUsageStore(BaseStore, Protocol):
    async def add_usage_points(self, person: Person, points: int) -> None:
        pass

    async def get_user_usage(self, person: Person) -> int:
        pass

    async def get_user_usage_report(self, person: Person) -> UserUsageRecord:
        pass

    async def get_user_usage_limit(self, person: Person) -> int:
        pass


class ChatsStore(BaseStore, Protocol):
    async def start_chat(self, context: Context) -> None:
        pass

    async def chat_is_started(self, context: Context) -> bool:
        pass

    async def stop_chat(self, context: Context) -> None:
        pass

    async def set_language(self, context: Context, language: str) -> None:
        pass

    async def get_language(self, context: Context) -> str:
        pass

    async def get_conversation_tracker_state(self, context: Context) -> bool:
        pass

    async def switch_conversation_tracker(self, context: Context) -> bool:
        pass

    async def get_auto_fact_state(self, context: Context) -> bool:
        pass

    async def switch_auto_fact(self, context: Context) -> bool:
        pass

    async def get_autoengage_state(self, context: Context) -> bool:
        pass

    async def switch_autoengage(self, context: Context) -> bool:
        pass

    async def get_memory_scope(self, context: Context, scope_key: str) -> dict:
        pass

    async def set_memory_scope(
        self, context: Context, scope_key: str, memory_scope: dict
    ) -> None:
        pass

    async def clear_memory(self, context: Context) -> None:
        pass


class UserFactsStore(BaseStore, Protocol):
    async def get_chat_facts(self, context: Context) -> List[Tuple[str, str]]:
        pass

    async def get_user_facts(self, context: Context, person: Person) -> List[str]:
        pass

    async def get_user_facts_by_participant(
        self,
        context: Context,
        participant_key: str,
        fallback_user_handle: Optional[str] = None,
    ) -> List[str]:
        pass

    async def get_facts_for_user_handle(
        self, context: Context, user_handle: str
    ) -> List[str]:
        pass

    async def add_fact(
        self,
        context: Context,
        facts_user_handle: str,
        fact: str,
        person: Optional[Person] = None,
        source_dialog_id: Optional[str] = None,
        created_by: str = "manual",
    ) -> None:
        pass

    async def clear_facts(self, context: Context, facts_user_handle: str) -> None:
        pass

    async def search_chat_facts(
        self,
        context: Context,
        query: Optional[str] = None,
        participant_key: Optional[str] = None,
    ) -> List[str]:
        pass


class UserIntroductionsStore(BaseStore, Protocol):
    async def add_introduction(
        self, context: Context, person: Person, introduction: str
    ) -> None:
        pass

    async def get_user_introduction(self, context: Context, person: Person) -> str:
        pass


class ChatModesStore(BaseStore, Protocol):
    async def get_chat_modes(self, context: Context) -> List[ChatModeRecord]:
        pass

    async def get_chat_mode(self, context: Context) -> ChatModeRecord:
        pass

    async def get_mode_name_by_id(self, context: Context, mode_id: str) -> str:
        pass

    async def set_chat_mode(self, context: Context, mode_id: str) -> None:
        pass

    async def delete_chat_mode(self, context: Context, mode_id: str) -> None:
        pass

    async def add_chat_mode(
        self,
        context: Context,
        mode_name: str,
        mode_description: str,
        added_by_handle: str,
    ) -> None:
        pass


class RecentDialogStore(BaseStore, Protocol):
    async def reset(self, context: Context) -> None:
        pass

    async def get_messages(
        self, context: Context
    ) -> List[Tuple[str, bool, TranscribedMessage]]:
        pass

    async def add_message_to_dialog(
        self,
        context: Context,
        person: Union[Person, Literal["bot"]],
        transcribed_message: TranscribedMessage,
        scope_key: Optional[str] = None,
        memory_role: Optional[str] = None,
        provider_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass

    async def search_recent_dialog(
        self,
        context: Context,
        query: Optional[str] = None,
        participant_key: Optional[str] = None,
        limit: int = 6,
    ) -> List[str]:
        pass
