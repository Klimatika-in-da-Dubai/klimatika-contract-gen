from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


ONE_TIME_CONTRACT_BUTTON_TEXT = "Разовый контракт"
YEAR_CONTRACT_BUTTON_TEXT = "Годовой контракт"


def get_doc_type_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=ONE_TIME_CONTRACT_BUTTON_TEXT),
                KeyboardButton(text=YEAR_CONTRACT_BUTTON_TEXT),
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите тип документа",
    )
