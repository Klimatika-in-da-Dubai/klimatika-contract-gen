from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from app.core.keyboards.back_keyboard import get_back_keyboard
from app.core.keyboards.date import get_date_choose_keyboard
from app.core.keyboards.service_count import get_service_count_keyboard

from app.core.states.states import YearContract


async def send_get_date_choose_message(func, state: FSMContext):
    await state.set_state(YearContract.get_date_choose)
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
        func, "Введите дату в формате:\nДЕНЬ МЕСЯЦ ГОД", YearContract.get_date, state
    )


async def send_get_address_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func, "Введите адрес клиента латиницей", YearContract.get_address, state
    )


async def send_get_client_name_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func, "Введите имя клиента латиницей", YearContract.get_client_name, state
    )


async def send_get_contract_number_cpm_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func,
        "Введите номер клиента из CPM",
        YearContract.get_contract_number_cpm,
        state,
    )


async def send_get_service1_date_choose_message(func, state: FSMContext):
    await state.set_state(YearContract.get_service1_date_choose)
    await func(
        "Дата 1-ого выезда - сегодня или более ранняя?",
        reply_markup=get_date_choose_keyboard(),
    )


async def send_get_service1_date_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func,
        "Введите дату 1-ого выезда в формате:\nДЕНЬ МЕСЯЦ ГОД",
        YearContract.get_service1_date,
        state,
    )


async def send_get_service1_price_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func, "Введите стоимость 1-ого выезда", YearContract.get_service1_price, state
    )


async def send_get_discount_message(func, state: FSMContext):
    await send_message_with_back_keyboard(
        func, "Введите размер скидки в процентах", YearContract.get_discount, state
    )


async def send_get_service_count_message(func, state: FSMContext):
    await state.set_state(YearContract.get_service_count)
    await func(
        "Выберите количество выездов в год", reply_markup=get_service_count_keyboard()
    )
