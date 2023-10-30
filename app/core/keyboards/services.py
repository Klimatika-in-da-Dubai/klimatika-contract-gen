from enum import IntEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.core.keyboards.back_keyboard import get_back_inline_button
from app.core.keyboards.enter import get_enter_inline_button

from app.core.middlewares.one_time_contract import (
    SERVICES_RU_NAME,
    OneTimeContractService,
)


class OneTimeContractServicesCB(CallbackData, prefix="services"):
    service: OneTimeContractService


def get_services_keyboard(services: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=get_service_text(services, OneTimeContractService.AC_MAINTENANCE),
            callback_data=OneTimeContractServicesCB(
                service=OneTimeContractService.AC_MAINTENANCE
            ).pack(),
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=get_service_text(services, OneTimeContractService.AC_REPAIR),
            callback_data=OneTimeContractServicesCB(
                service=OneTimeContractService.AC_REPAIR
            ).pack(),
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=get_service_text(services, OneTimeContractService.OTHER),
            callback_data=OneTimeContractServicesCB(
                service=OneTimeContractService.OTHER
            ).pack(),
        )
    )
    builder.row(get_back_inline_button(), get_enter_inline_button())
    return builder.as_markup()


def get_service_text(services: dict, service: OneTimeContractService) -> str:
    if service not in services:
        return f"{SERVICES_RU_NAME[service].capitalize()}: ❌"

    if services[service] == 0:
        return f"{SERVICES_RU_NAME[service].capitalize()}: ❌"

    return f"{SERVICES_RU_NAME[service].capitalize()}: {services[service]:.2f} ✅"


class UpdateServiceTarget(IntEnum):
    CHANGE = auto()
    DELETE = auto()


class UpdateServiceCB(CallbackData, prefix="service"):
    target: UpdateServiceTarget


def get_service_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="Изменить",
            callback_data=UpdateServiceCB(target=UpdateServiceTarget.CHANGE).pack(),
        )
    )

    builder.row(
        InlineKeyboardButton(
            text="Удалить",
            callback_data=UpdateServiceCB(target=UpdateServiceTarget.DELETE).pack(),
        )
    )

    builder.row(get_back_inline_button())
    return builder.as_markup()
