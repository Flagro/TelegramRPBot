from telegram import (
    Update,
    User,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    AIORateLimiter,
    filters,
)
from telegram.constants import ParseMode, ChatAction

from typing import List

from .db.db import ChatModeResponse


def get_chat_modes_keyboard(
    chat_modes: List[ChatModeResponse], page_index: int, modes_per_page: int
) -> InlineKeyboardMarkup:
    # chat modes
    modes = []
    for chat_mode in chat_modes[
        page_index * modes_per_page : (page_index + 1) * modes_per_page
    ]:
        modes.append(
            InlineKeyboardButton(
                chat_mode.mode_name, callback_data=f"set_chat_mode|{chat_mode.id}"
            )
        )

    # pagination
    pagination = []
    if len(chat_modes) > modes_per_page:
        if page_index != 0:
            pagination.append(
                InlineKeyboardButton(
                    "«", callback_data=f"show_chat_modes|{page_index - 1}"
                )
            )
        if (page_index + 1) * modes_per_page < len(chat_modes):
            pagination.append(
                InlineKeyboardButton(
                    "»", callback_data=f"show_chat_modes|{page_index + 1}"
                )
            )

    keyboard = [[mode] for mode in modes] + [pagination]
    keyboard_markup = InlineKeyboardMarkup(keyboard)

    return keyboard_markup
