from typing import Optional, Any, List

import pymongo
import config
from collections import namedtuple


UserUsageResponse = namedtuple("UserUsageResponse", ["this_month_usage", "limit"])
ChatModeResponse = namedtuple("ChatModesResponse", ["id", "mode_name", "mode_description"])


class DB:
    def __init__(self):
        self.client = pymongo.MongoClient(config.mongodb_uri)
        self.db = self.client["chatgpt_telegram_bot"]

        self.user_collection = self.db["user"]
        self.dialog_collection = self.db["dialog"]

    def get_user_usage(self, user_handle: str) -> UserUsageResponse:
        user = self.user_collection.find_one({"handle": user_handle})
        if not user:
            return UserUsageResponse(0, config.default_monthly_limit)

        return UserUsageResponse(user["this_month_usage"], user["limit"])
    
    def get_chat_modes(self, chat_id: str) -> List[ChatModeResponse]:
        chat = self.dialog_collection.find_one({"chat_id": chat_id})
        if not chat:
            return []

        return [
            ChatModeResponse(mode["id"], mode["mode_name"], mode["mode_description"])
            for mode in chat["chat_modes"]
        ]
