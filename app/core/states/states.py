from aiogram.fsm.state import State, StatesGroup


class OneTimeContract(StatesGroup):
    get_date_choose = State()
    get_date = State()
    get_address = State()
    get_client_name = State()
    get_contract_number_cpm = State()
    get_service = State()
    update_service = State()
    get_service_price = State()
    get_discount = State()


class YearContract(StatesGroup):
    get_date_choose = State()
    get_date = State()
    get_address = State()
    get_client_name = State()
    get_contract_number_cpm = State()
    get_service1_date_choose = State()
    get_service1_date = State()
    get_service1_price = State()
    get_others_price = State()
    get_discount = State()
    get_service_count = State()
