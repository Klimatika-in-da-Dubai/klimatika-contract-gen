from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.back_keyboard import get_back_inline_button

TODAY_DATE_BUTTON_TEXT = "Сегодня"
EARLIER_DATE_BUTTON_TEXT = "Более ранняя"
LATER_DATE_BUTTON_TEXT = "Более поздняя"


class DateChooseTarget(IntEnum):
    TODAY = auto()
    EARLIER = auto()
    LATER = auto()


class DateChooseCB(CallbackData, prefix="date_input_type"):
    target: DateChooseTarget


def get_date_choose_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=EARLIER_DATE_BUTTON_TEXT,
            callback_data=DateChooseCB(target=DateChooseTarget.EARLIER).pack(),
        ),
        InlineKeyboardButton(
            text=TODAY_DATE_BUTTON_TEXT,
            callback_data=DateChooseCB(target=DateChooseTarget.TODAY).pack(),
        ),
        InlineKeyboardButton(
            text=LATER_DATE_BUTTON_TEXT,
            callback_data=DateChooseCB(target=DateChooseTarget.LATER).pack(),
        ),
    )
    builder.row(get_back_inline_button())
    return builder.as_markup()

# def get_date_choose_keyboard_from_check_out() -> InlineKeyboardMarkup:
#     builder = InlineKeyboardBuilder()
#     builder.row(
#         InlineKeyboardButton(
#             text=EARLIER_DATE_BUTTON_TEXT,
#             callback_data=DateChooseCB(target=DateChooseTarget.EARLIER).pack(),
#         ),
#         InlineKeyboardButton(
#             text=TODAY_DATE_BUTTON_TEXT,
#             callback_data=DateChooseCB(target=DateChooseTarget.TODAY).pack(),
#         ),
#         InlineKeyboardButton(
#             text=LATER_DATE_BUTTON_TEXT,
#             callback_data=DateChooseCB(target=DateChooseTarget.LATER).pack(),
#         ),
#     )
#     builder.row(get_back_inline_button())
#     return builder.as_markup()