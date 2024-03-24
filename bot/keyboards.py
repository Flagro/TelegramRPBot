from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from typing import List
from .db.db import ChatModeResponse


def get_chat_modes_keyboard(
    chat_modes: List[ChatModeResponse],
    page_index: int,
    modes_per_page: int,
    action: str,
) -> InlineKeyboardMarkup:
    page_start = page_index * modes_per_page
    page_end = (page_index + 1) * modes_per_page

    # chat modes
    modes = []
    for chat_mode in chat_modes[page_start:page_end]:
        modes.append(
            InlineKeyboardButton(
                chat_mode.mode_name, callback_data=f"{action}|{chat_mode.id}"
            )
        )

    # pagination
    pagination = []
    if page_start > 0:
        pagination.append(
            InlineKeyboardButton("«", callback_data=f"show_chat_modes|{page_index - 1}")
        )
    if page_end < len(chat_modes):
        pagination.append(
            InlineKeyboardButton("»", callback_data=f"show_chat_modes|{page_index + 1}")
        )

    keyboard = [[mode] for mode in modes] + [pagination]
    keyboard_markup = InlineKeyboardMarkup(keyboard)

    return keyboard_markup
