from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.keyboards.back_keyboard import get_back_inline_button


class ServiceCountCB(CallbackData, prefix="service_count"):
    count: int


def get_service_count_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="2", callback_data=ServiceCountCB(count=2).pack()),
        InlineKeyboardButton(text="3", callback_data=ServiceCountCB(count=3).pack()),
        InlineKeyboardButton(text="4", callback_data=ServiceCountCB(count=4).pack()),
    )

    builder.row(get_back_inline_button())
    return builder.as_markup()
