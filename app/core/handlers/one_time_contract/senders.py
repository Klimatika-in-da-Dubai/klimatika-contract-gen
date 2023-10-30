from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from app.core.keyboards.back_keyboard import get_back_keyboard
from app.core.keyboards.date import get_date_choose_keyboard
from app.core.keyboards.services import get_service_keyboard, get_services_keyboard
from app.core.middlewares.one_time_contract import (
    SERVICES_RU_NAME,
    OneTimeContractService,
    OneTimeContractStateData,
)

from app.core.states.states import OneTimeContract


async def send_get_date_choose_message(func, state: FSMContext):
    await state.set_state(OneTimeContract.get_date_choose)
    await func(
        text="Дата заключения - сегодня или более ранняя?",
        reply_markup=get_date_choose_keyboard(),
    )


async def send_message_with_back_keyboard(
    func, text: str, set_state: State, state: FSMContext
):
    await state.set_state(set_state)
    await func(text=text, reply_markup=get_back_keyboard())


async def send_get_date_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func, "Введите дату в формате:\nДЕНЬ МЕСЯЦ ГОД", OneTimeContract.get_date, state
    )


async def send_get_address_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func, "Введите адрес клиента латиницей", OneTimeContract.get_address, state
    )


async def send_get_client_name_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func, "Введите имя клиента латиницей", OneTimeContract.get_client_name, state
    )


async def send_get_contract_number_cpm_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func,
        "Введите номер клиента из CPM",
        OneTimeContract.get_contract_number_cpm,
        state,
    )


async def send_get_services_message(
    func,
    state: FSMContext,
):
    await state.set_state(OneTimeContract.get_service)
    services = await OneTimeContractStateData(state).get_services()
    await func(
        "Выберите нужные сервисы и укажите для них размер оплаты",
        reply_markup=get_services_keyboard(services),
    )


async def send_get_service_price_message(
    func, state: FSMContext, service: OneTimeContractService
):
    await send_message_with_back_keyboard(
        func,
        f"Введите сумму оплаты за {SERVICES_RU_NAME[service]}",
        OneTimeContract.get_service_price,
        state,
    )


async def send_update_service_message(
    func, state: FSMContext, service: OneTimeContractService
):
    await state.set_state(OneTimeContract.update_service)
    price = await OneTimeContractStateData(state).get_service_price(service)
    await func(
        f"{SERVICES_RU_NAME[service]}\n" f"Цена: {price}",
        reply_markup=get_service_keyboard(),
    )


async def send_get_discount_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func,
        "Введите размер скидки в процентах",
        OneTimeContract.get_discount,
        state,
    )
