import logging
import os
from pathlib import Path
from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from datetime import date
from app.core.handlers.main import send_choose_doc_type_message
from app.core.handlers.year_contract.senders import (
    send_get_address_message,
    send_get_client_name_message,
    send_get_contract_number_cpm_message,
    send_get_date_choose_message,
    send_get_date_message,
    send_get_discount_message,
    send_get_service1_date_choose_message,
    send_get_service1_date_message,
    send_get_service1_price_message,
    send_get_service_count_message,
)
from app.core.keyboards.back_keyboard import BackCB
from app.core.keyboards.date import DateChooseCB, DateChooseTarget
from app.core.keyboards.doc_type import YEAR_CONTRACT_BUTTON_TEXT, get_doc_type_keyboard
from app.core.keyboards.service_count import ServiceCountCB
from app.core.middlewares.year_contract import (
    YearContractMiddleware,
    YearContractStateData,
)
from app.core.states.states import YearContract
from app.services.docs_gen.year_contract import YearContractPDF


year_contract_router = Router()

year_contract_router.message.middleware(YearContractMiddleware())
year_contract_router.callback_query.middleware(YearContractMiddleware())


@year_contract_router.message(F.text == YEAR_CONTRACT_BUTTON_TEXT)
async def year_contract_chosen(
    message: Message, state: FSMContext, year_contract: YearContractStateData
):
    await state.clear()
    await year_contract.init()
    await send_get_date_choose_message(message.answer, state)


@year_contract_router.callback_query(
    YearContract.get_date_choose,
    DateChooseCB.filter(F.target == DateChooseTarget.TODAY),
)
async def get_date_today(
    cb: CallbackQuery, state: FSMContext, year_contract: YearContractStateData
):
    await cb.answer()
    today_date = date.today()
    await year_contract.set_date(today_date)
    await send_get_address_message(cb.message.edit_text, state)  # type: ignore


@year_contract_router.callback_query(
    YearContract.get_date_choose,
    DateChooseCB.filter(F.target == DateChooseTarget.EARLIER),
)
async def get_earlier_date(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await send_get_date_message(cb.message.edit_text, state)  # type: ignore


@year_contract_router.message(YearContract.get_date, F.text)
async def get_date_message(
    message: Message, state: FSMContext, year_contract: YearContractStateData
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
    await year_contract.set_date(input_date)
    await send_get_address_message(message.answer, state)


@year_contract_router.message(YearContract.get_address, F.text)
async def get_address_message(
    message: Message, state: FSMContext, year_contract: YearContractStateData
):
    assert message.text is not None
    await year_contract.set_address(message.text)
    await send_get_client_name_message(message.answer, state)


@year_contract_router.message(YearContract.get_client_name, F.text)
async def get_client_name_message(
    message: Message, state: FSMContext, year_contract: YearContractStateData
):
    assert message.text is not None
    await year_contract.set_client_name(message.text)
    await send_get_contract_number_cpm_message(message.answer, state)


@year_contract_router.message(YearContract.get_contract_number_cpm, F.text)
async def get_contract_number_cpm_message(
    message: Message, state: FSMContext, year_contract: YearContractStateData
):
    assert message.text is not None
    await year_contract.set_contract_number_cpm(message.text)
    await send_get_service1_date_choose_message(message.answer, state)


@year_contract_router.callback_query(
    YearContract.get_service1_date_choose,
    DateChooseCB.filter(F.target == DateChooseTarget.TODAY),
)
async def get_service1_date_today(
    cb: CallbackQuery, state: FSMContext, year_contract: YearContractStateData
):
    await cb.answer()
    today_date = date.today()
    await year_contract.set_service1_date(today_date)
    await send_get_service1_price_message(cb.message.edit_text, state)  # type: ignore


@year_contract_router.callback_query(
    YearContract.get_service1_date_choose,
    DateChooseCB.filter(F.target == DateChooseTarget.EARLIER),
)
async def get_earlier_service_date(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await send_get_service1_date_message(cb.message.edit_text, state)  # type: ignore


@year_contract_router.message(YearContract.get_service1_date, F.text)
async def get_service1_date_message(
    message: Message, state: FSMContext, year_contract: YearContractStateData
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
    await year_contract.set_service1_date(input_date)
    await send_get_service1_price_message(message.answer, state)


@year_contract_router.message(YearContract.get_service1_price, F.text)
async def get_service1_price_message(
    message: Message, state: FSMContext, year_contract: YearContractStateData
):
    assert message.text is not None
    text = message.text.replace(",", ".")
    if not text.isnumeric():
        await message.answer("Введите число!")
        return

    await year_contract.set_service1_price(float(message.text))
    await send_get_discount_message(message.answer, state)


@year_contract_router.message(YearContract.get_discount, F.text)
async def get_discount_price_message(
    message: Message, state: FSMContext, year_contract: YearContractStateData
):
    assert message.text is not None
    text = message.text.replace(",", ".")
    if not text.isnumeric():
        await message.answer("Введите число!")
        return

    await year_contract.set_discount(float(message.text))
    await send_get_service_count_message(message.answer, state)


@year_contract_router.callback_query(
    YearContract.get_service_count, ServiceCountCB.filter()
)
async def cb_get_service_count(
    cb: CallbackQuery,
    callback_data: ServiceCountCB,
    state: FSMContext,
    year_contract: YearContractStateData,
):
    await cb.answer()
    await year_contract.set_service_count(callback_data.count)  # type: ignore
    await generate_and_send_year_contract_pdf(cb.message, year_contract)  # type: ignore
    await state.clear()


async def generate_and_send_year_contract_pdf(
    message: Message, year_contract: YearContractStateData
):
    await message.answer("Генерирую отчёт...")  # type: ignore
    print(await year_contract.get_year_contract())
    try:
        path = YearContractPDF(
            data=await year_contract.get_year_contract_data()
        ).generate_pdf(Path("."), str(message.chat.id))
    except Exception as e:
        logging.error(e)
        await message.answer("Произошла ошибка пожалуйста обратитесь к администратору!")  # type: ignore
        return

    await message.answer_document(FSInputFile(path), caption="Ваш отчёт!", reply_markup=get_doc_type_keyboard())  # type: ignore
    os.remove(path)


@year_contract_router.callback_query(
    or_f(
        YearContract.get_date_choose,
        YearContract.get_date,
        YearContract.get_address,
        YearContract.get_client_name,
        YearContract.get_contract_number_cpm,
        YearContract.get_service1_date_choose,
        YearContract.get_service1_date,
        YearContract.get_service1_price,
        YearContract.get_discount,
        YearContract.get_service_count,
    ),
    BackCB.filter(),
)
async def cb_back(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    match await state.get_state():
        case YearContract.get_date_choose.state:
            await cb.message.delete()  # type: ignore
            await send_choose_doc_type_message(cb.message.answer, state)  # type: ignore
            return
        case YearContract.get_date.state:
            func = send_get_date_choose_message
        case YearContract.get_address.state:
            func = send_get_date_choose_message
        case YearContract.get_client_name.state:
            func = send_get_address_message
        case YearContract.get_contract_number_cpm.state:
            func = send_get_client_name_message
        case YearContract.get_service1_date_choose.state:
            func = send_get_contract_number_cpm_message
        case YearContract.get_service1_date.state:
            func = send_get_service1_date_choose_message
        case YearContract.get_service1_price.state:
            func = send_get_service1_date_choose_message
        case YearContract.get_discount.state:
            func = send_get_service1_price_message
        case YearContract.get_service_count.state:
            func = send_get_discount_message

    await func(cb.message.edit_text, state)  # type: ignore
