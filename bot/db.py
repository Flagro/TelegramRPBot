from typing import Optional, Any, List
from uuid import UUID

import pymongo
from collections import namedtuple


UserUsageResponse = namedtuple("UserUsageResponse", ["this_month_usage", "limit"])
ChatModeResponse = namedtuple(
    "ChatModesResponse", ["id", "mode_name", "mode_description"]
)


class DB:
    def __init__(self, uri: str, db_config: Any, default_chat_modes: Any):
        self.client = pymongo.MongoClient(uri)

    def create_user_if_not_exists(self, user_handle: str) -> None:
        pass

    def set_language(self, chat_id: str, language: str) -> None:
        pass

    def get_user_usage(self, user_handle: str) -> UserUsageResponse:
        pass

    def get_chat_modes(self, chat_id: str) -> List[ChatModeResponse]:
        pass

    def set_chat_mode(self, chat_id: str, mode_id: UUID) -> None:
        pass

    def delete_chat_mode(self, chat_id: str, mode_id: UUID) -> None:
        pass

    def add_chat_mode(
        self, chat_id: str, mode_name: str, mode_description: str
    ) -> None:
        pass

    def add_introduction(
        self, chat_id: str, user_handle: str, introduction: str
    ) -> None:
        pass

    def add_fact(self, chat_id: str, facts_user_handle: str, facts: str) -> None:
        pass

    def clear_facts(self, chat_id: str, facts_user_handle: str) -> None:
        pass

    def reset(self, chat_id: str) -> None:
        pass
    
    def save_thread_message(
        self, thread_id: Optional[str], user_handle: str, message: str
    ) -> None:
        pass

    def add_user_input_to_dialog(
        self,
        chat_id: str,
        user_handle: str,
        message: str,
        image_description: str,
        voice_description: str,
    ) -> None:
        pass

    def add_bot_response_to_dialog(
        self, chat_id: str, bot_response: str, response_image_url: str
    ) -> None:
        pass
