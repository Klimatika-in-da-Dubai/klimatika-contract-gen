from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.core.keyboards.doc_type import get_doc_type_keyboard


main_router = Router()


@main_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await send_choose_doc_type_message(message.answer, state)


async def send_choose_doc_type_message(func, state: FSMContext):
    await state.clear()
    await func("Выберите нужный тип документа", reply_markup=get_doc_type_keyboard())
