from ...models.base_handlers import BaseCallbackHandler
from ...models.handlers_response import CommandResponse
from ..db import ChatModeResponse
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from typing import List, Optional


def get_chat_modes_keyboard(
    chat_modes: List[ChatModeResponse],
    callback: str,
    button_action: str,
    page_index: Optional[int] = 0,
    modes_per_page: Optional[int] = 5,
) -> InlineKeyboardMarkup:
    page_start = page_index * modes_per_page
    page_end = (page_index + 1) * modes_per_page

    # chat modes
    modes = []
    for chat_mode in chat_modes[page_start:page_end]:
        modes.append(
            InlineKeyboardButton(
                chat_mode.mode_name, callback_data=f"{button_action}|{chat_mode.id}"
            )
        )

    # pagination
    pagination = []
    if page_start > 0:
        pagination.append(
            InlineKeyboardButton("«", callback_data=f"{callback}|{button_action}|{page_index - 1}")
        )
    if page_end < len(chat_modes):
        pagination.append(
            InlineKeyboardButton("»", callback_data=f"{callback}|{button_action}|{page_index + 1}")
        )

    keyboard = [[mode] for mode in modes] + [pagination]
    keyboard_markup = InlineKeyboardMarkup(keyboard)

    return keyboard_markup


class CallbackHandler(BaseCallbackHandler):
    pattern = "^show_chat_modes"
    
    async def handle(self, chat_id, args) -> CommandResponse:
        button_action = args[0]
        page_index = int(args[1])
        available_modes = self.db.get_chat_modes(chat_id)
        modes_keyboard = get_chat_modes_keyboard(
            available_modes, "show_chat_modes", button_action, page_index
        )
        return CommandResponse("", {}, modes_keyboard)
