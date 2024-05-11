from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from uuid import UUID
from typing import List, Optional


def get_paginated_list_keyboard(
    value_names: List[str],
    value_ids: List[UUID],
    callback: str,
    button_action: str,
    page_index: Optional[int] = 0,
    modes_per_page: Optional[int] = 5,
) -> InlineKeyboardMarkup:
    values = list(zip(value_names, value_ids))
    page_start = page_index * modes_per_page
    page_end = (page_index + 1) * modes_per_page

    # chat modes
    modes = []
    for value in values[page_start:page_end]:
        modes.append(
            InlineKeyboardButton(
                value[0], callback_data=f"{button_action}|{value[1]}"
            )
        )

    # pagination
    pagination = []
    if page_start > 0:
        pagination.append(
            InlineKeyboardButton("«", callback_data=f"{callback}|{button_action}|{page_index - 1}")
        )
    if page_end < len(values):
        pagination.append(
            InlineKeyboardButton("»", callback_data=f"{callback}|{button_action}|{page_index + 1}")
        )

    keyboard = [[mode] for mode in modes] + [pagination]
    keyboard_markup = InlineKeyboardMarkup(keyboard)

    return keyboard_markup
