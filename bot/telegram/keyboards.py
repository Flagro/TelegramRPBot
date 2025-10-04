from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from uuid import UUID
from typing import Optional
from collections import OrderedDict


def get_paginated_list_keyboard(
    value_id_to_name: OrderedDict[UUID, str],
    callback: str,
    button_action: str,
    page_index: Optional[int] = 0,
    modes_per_page: Optional[int] = 5,
) -> InlineKeyboardMarkup:
    value_names = list(value_id_to_name.values())
    values = list(
        zip(map(lambda s: s.capitalize(), value_names), value_id_to_name.keys())
    )
    page_start = page_index * modes_per_page
    page_end = (page_index + 1) * modes_per_page

    # chat modes
    modes = []
    for value in values[page_start:page_end]:
        modes.append(
            InlineKeyboardButton(value[0], callback_data=f"{button_action}|{value[1]}")
        )

    # pagination
    pagination = []
    if page_start > 0:
        pagination.append(
            InlineKeyboardButton(
                "«", callback_data=f"{callback}|{button_action}|{page_index - 1}"
            )
        )
    if page_end < len(values):
        pagination.append(
            InlineKeyboardButton(
                "»", callback_data=f"{callback}|{button_action}|{page_index + 1}"
            )
        )

    keyboard = [[mode] for mode in modes] + [pagination]
    keyboard_markup = InlineKeyboardMarkup(keyboard)

    return keyboard_markup
