import logging
from pathlib import Path
from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from datetime import date
import os
from app.core.handlers.main import send_choose_doc_type_message
from app.core.handlers.one_time_contract.senders import (
    send_get_ac_maintenance_price_message,
    send_get_ac_repair_price_message,
    send_get_address_message,
    send_get_client_name_message,
    send_get_contract_number_cpm_message,
    send_get_date_choose_message,
    send_get_date_message,
    send_get_discount_price_message,
    send_get_other_price_message,
)
from app.core.keyboards.back_keyboard import BackCB

from app.core.keyboards.date import (
    DateChooseCB,
    DateChooseTarget,
)

from app.core.keyboards.doc_type import (
    ONE_TIME_CONTRACT_BUTTON_TEXT,
    get_doc_type_keyboard,
)
from app.core.middlewares.one_time_contract import (
    OneTimeContractMiddleware,
    OneTimeContractStateData,
)
from app.core.states.states import OneTimeContract
from app.services.docs_gen.one_time_contract import OneTimeContractPDF


one_time_contract_router = Router()
one_time_contract_router.message.middleware(OneTimeContractMiddleware())
one_time_contract_router.callback_query.middleware(OneTimeContractMiddleware())


@one_time_contract_router.message(F.text == ONE_TIME_CONTRACT_BUTTON_TEXT)
async def one_time_contract_chosen(
    message: Message, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    await state.clear()
    await one_time_contract.init()
    await send_get_date_choose_message(message.answer, state)


@one_time_contract_router.callback_query(
    OneTimeContract.get_date_choose,
    DateChooseCB.filter(F.target == DateChooseTarget.TODAY),
)
async def get_date_today(
    cb: CallbackQuery, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    await cb.answer()
    today_date = date.today()
    await one_time_contract.set_date(today_date)
    await send_get_address_message(cb.message.edit_text, state)  # type: ignore


@one_time_contract_router.callback_query(
    OneTimeContract.get_date_choose,
    DateChooseCB.filter(F.target == DateChooseTarget.EARLIER),
)
async def get_earlier_date(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await send_get_date_message(cb.message.edit_text, state)  # type: ignore


@one_time_contract_router.message(OneTimeContract.get_date, F.text)
async def get_date_message(
    message: Message, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    date_parts = message.text.split()  # type: ignore
    if len(date_parts) != 3 or not all(part.isnumeric() for part in date_parts):
        await message.answer("Некорректный ввод")
        return

    day, month, year = date_parts
    if len(year) == 2:
        year = "20" + year

    try:
        input_date = date(int(year), int(month), int(day))
    except Exception:
        await message.answer("Некорректная дата")
        return
    await one_time_contract.set_date(input_date)
    await send_get_address_message(message.answer, state)


@one_time_contract_router.message(OneTimeContract.get_address, F.text)
async def get_address_message(
    message: Message, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    assert message.text is not None
    await one_time_contract.set_address(message.text)
    await send_get_client_name_message(message.answer, state)


@one_time_contract_router.message(OneTimeContract.get_client_name, F.text)
async def get_client_name_message(
    message: Message, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    assert message.text is not None
    await one_time_contract.set_client_name(message.text)
    await send_get_contract_number_cpm_message(message.answer, state)


@one_time_contract_router.message(OneTimeContract.get_contract_number_cpm, F.text)
async def get_contract_number_cpm_message(
    message: Message, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    assert message.text is not None
    await one_time_contract.set_contract_number_cpm(message.text)
    await send_get_ac_maintenance_price_message(message.answer, state)


@one_time_contract_router.message(OneTimeContract.get_ac_maintenance_price, F.text)
async def get_ac_maintenance_price_message(
    message: Message, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    assert message.text is not None
    text = message.text.replace(",", ".")
    if not text.isnumeric():
        await message.answer("Введите число!")
        return

    await one_time_contract.set_ac_maintenance_price(float(message.text))
    await send_get_ac_repair_price_message(message.answer, state)


@one_time_contract_router.message(OneTimeContract.get_ac_repair_price, F.text)
async def get_ac_repair_price_message(
    message: Message,
    state: FSMContext,
    one_time_contract: OneTimeContractStateData,
):
    assert message.text is not None
    text = message.text.replace(",", ".")
    if not text.isnumeric():
        await message.answer("Введите число!")
        return

    await one_time_contract.set_ac_repair_price(float(message.text))
    await send_get_other_price_message(message.answer, state)


@one_time_contract_router.message(OneTimeContract.get_other_price, F.text)
async def get_other_price_message(
    message: Message, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    assert message.text is not None
    text = message.text.replace(",", ".")
    if not text.isnumeric():
        await message.answer("Введите число!")
        return

    await one_time_contract.set_other_price(float(message.text))
    await send_get_discount_price_message(message.answer, state)


@one_time_contract_router.message(OneTimeContract.get_discount_price, F.text)
async def get_discount_price_message(
    message: Message, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    assert message.text is not None
    text = message.text.replace(",", ".")
    if not text.isnumeric():
        await message.answer("Введите число!")
        return

    await one_time_contract.set_discount_price(float(message.text))

    await generate_and_send_one_time_contract_pdf(message, one_time_contract)
    await state.clear()


async def generate_and_send_one_time_contract_pdf(
    message: Message, one_time_contract: OneTimeContractStateData
):
    await message.answer("Генерирую отчёт...")  # type: ignore
    try:
        path = OneTimeContractPDF(
            data=await one_time_contract.get_one_time_contract_data()
        ).generate_pdf(Path("."), str(message.chat.id))
    except Exception as e:
        logging.error(e)
        await message.answer("Произошла ошибка пожалуйста обратитесь к администратору!")  # type: ignore
        return

    await message.answer_document(FSInputFile(path), caption="Ваш отчёт!", reply_markup=get_doc_type_keyboard())  # type: ignore
    os.remove(path)


@one_time_contract_router.callback_query(
    or_f(
        OneTimeContract.get_date_choose,
        OneTimeContract.get_date,
        OneTimeContract.get_address,
        OneTimeContract.get_client_name,
        OneTimeContract.get_contract_number_cpm,
        OneTimeContract.get_ac_maintenance_price,
        OneTimeContract.get_ac_repair_price,
        OneTimeContract.get_other_price,
        OneTimeContract.get_discount_price,
    ),
    BackCB().filter(),
)
async def cb_back(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    match state.get_state():
        case OneTimeContract.get_date_choose.state:
            await cb.message.delete()  # type: ignore
            await send_choose_doc_type_message(cb.message.answer, state)  # type: ignore
            return
        case OneTimeContract.get_date.state:
            func = send_get_date_choose_message
        case OneTimeContract.get_address.state:
            func = send_get_date_choose_message
        case OneTimeContract.get_client_name.state:
            func = send_get_address_message
        case OneTimeContract.get_contract_number_cpm.state:
            func = send_get_client_name_message
        case OneTimeContract.get_ac_maintenance_price.state:
            func = send_get_contract_number_cpm_message
        case OneTimeContract.get_ac_repair_price.state:
            func = send_get_ac_maintenance_price_message
        case OneTimeContract.get_other_price.state:
            func = send_get_ac_repair_price_message
        case OneTimeContract.get_discount_price.state:
            func = send_get_other_price_message

    await func(cb.message.edit_text, state)  # type: ignore
