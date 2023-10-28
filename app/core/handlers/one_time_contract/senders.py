from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from app.core.keyboards.back_keyboard import get_back_keyboard
from app.core.keyboards.date import get_date_choose_keyboard

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


async def send_get_ac_maintenance_price_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func,
        "Введите стоимость услуг по обслуживанию кондиционера",
        OneTimeContract.get_ac_maintenance_price,
        state,
    )


async def send_get_ac_repair_price_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func,
        "Введите стоимость услуг по ремонту",
        OneTimeContract.get_ac_repair_price,
        state,
    )


async def send_get_other_price_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func,
        "Введите стоимость иных услуг",
        OneTimeContract.get_other_price,
        state,
    )


async def send_get_discount_price_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func, "Введите стоимость скидки", OneTimeContract.get_discount_price, state
    )
