import logging
from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from datetime import date
from app.core.handlers.main import send_choose_doc_type_message
from app.core.handlers.one_time_contract.senders import (
    send_get_address_message,
    send_get_client_name_message,
    send_get_contract_number_cpm_message,
    send_get_date_choose_message,
    send_get_date_message,
    send_get_discount_message,
    send_get_service_price_message,
    send_get_services_message,
    send_update_service_message,
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
from app.core.keyboards.enter import EnterCB
from app.core.keyboards.services import (
    OneTimeContractServicesCB,
    UpdateServiceCB,
    UpdateServiceTarget,
)
from app.core.middlewares.one_time_contract import (
    OneTimeContractMiddleware,
    OneTimeContractStateData,
)
from app.core.states.states import OneTimeContract
from app.services.docs_gen.one_time_contract import OneTimeContractPDF
from app.settings.config import PATH_TO_REPORTS


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
    await send_get_services_message(message.answer, state)


@one_time_contract_router.callback_query(
    OneTimeContract.get_service,
    OneTimeContractServicesCB.filter(),
)
async def cb_get_service(
    cb: CallbackQuery,
    callback_data: OneTimeContractServicesCB,
    state: FSMContext,
    one_time_contract: OneTimeContractStateData,
):
    await cb.answer()
    await one_time_contract.set_selected_service(callback_data.service)

    if not await one_time_contract.is_service_in_services(callback_data.service):
        await send_get_service_price_message(
            cb.message.edit_text, state, callback_data.service  # type: ignore
        )
        return

    await send_update_service_message(
        cb.message.edit_text, state, callback_data.service  # type: ignore
    )


@one_time_contract_router.message(OneTimeContract.get_service_price, F.text)
async def get_other_price_message(
    message: Message, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    assert message.text is not None
    text = message.text.replace(",", ".")
    if not text.isnumeric():
        await message.answer("Введите число!")
        return
    selected_service = await one_time_contract.get_selected_service()

    await one_time_contract.set_service_price(selected_service, float(message.text))
    await one_time_contract.unselect_service()
    await send_get_services_message(message.answer, state)


@one_time_contract_router.callback_query(OneTimeContract.get_service, EnterCB.filter())
async def cb_enter(
    cb: CallbackQuery, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    services = await one_time_contract.get_services()
    if len(list(services.keys())) == 0 or not all(
        [services[service] for service in services]
    ):
        await cb.answer(text="Заполните хотя бы один сервис!", show_alert=True)
        return

    await cb.answer()
    await send_get_discount_message(cb.message.edit_text, state)  # type: ignore


@one_time_contract_router.callback_query(
    OneTimeContract.update_service,
    UpdateServiceCB.filter(F.target == UpdateServiceTarget.CHANGE),
)
async def cb_change_service_price(
    cb: CallbackQuery, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    await cb.answer()
    service = await one_time_contract.get_selected_service()
    await send_get_service_price_message(cb.message.edit_text, state, service)  # type: ignore


@one_time_contract_router.callback_query(
    OneTimeContract.update_service,
    UpdateServiceCB.filter(F.target == UpdateServiceTarget.DELETE),
)
async def cb_delete_service(
    cb: CallbackQuery, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    await cb.answer()
    service = await one_time_contract.get_selected_service()
    await one_time_contract.remove_service(service)
    await send_get_services_message(cb.message.edit_text, state)  # type: ignore


@one_time_contract_router.message(OneTimeContract.get_discount, F.text)
async def get_discount_message(
    message: Message, state: FSMContext, one_time_contract: OneTimeContractStateData
):
    assert message.text is not None
    text = message.text.replace(",", ".")
    if not text.isnumeric():
        await message.answer("Введите число!")
        return

    await one_time_contract.set_discount(float(message.text))

    await generate_and_send_one_time_contract_pdf(message, one_time_contract)
    await state.clear()


async def generate_and_send_one_time_contract_pdf(
    message: Message, one_time_contract: OneTimeContractStateData
):
    await message.answer("Генерирую отчёт...")  # type: ignore
    try:
        path = OneTimeContractPDF(
            data=await one_time_contract.get_one_time_contract_data()
        ).generate_pdf(PATH_TO_REPORTS, str(message.chat.first_name))
    except Exception as e:
        logging.error(e)
        await message.answer("Произошла ошибка пожалуйста обратитесь к администратору!")  # type: ignore
        return

    await message.answer_document(FSInputFile(path), caption="Ваш отчёт!", reply_markup=get_doc_type_keyboard())  # type: ignore


@one_time_contract_router.callback_query(
    or_f(
        OneTimeContract.get_date_choose,
        OneTimeContract.get_date,
        OneTimeContract.get_address,
        OneTimeContract.get_client_name,
        OneTimeContract.get_contract_number_cpm,
        OneTimeContract.get_service,
        OneTimeContract.get_service_price,
        OneTimeContract.update_service,
    ),
    BackCB().filter(),
)
async def cb_back(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    match await state.get_state():
        case OneTimeContract.get_date_choose.state:
            await cb.message.delete()  # type: ignore
            await send_choose_doc_type_message(cb.message.answer, state)  # type: ignore
            return
        case OneTimeContract.get_date.state | OneTimeContract.get_address.state:
            func = send_get_date_choose_message
        case OneTimeContract.get_client_name.state:
            func = send_get_address_message
        case OneTimeContract.get_contract_number_cpm.state:
            func = send_get_client_name_message
        case OneTimeContract.get_service.state:
            func = send_get_contract_number_cpm_message
        case OneTimeContract.get_service_price.state | OneTimeContract.update_service.state | OneTimeContract.get_discount:
            func = send_get_services_message

    await func(cb.message.edit_text, state)  # type: ignore
