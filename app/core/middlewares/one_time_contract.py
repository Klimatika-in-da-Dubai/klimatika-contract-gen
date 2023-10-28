from collections.abc import Awaitable, Callable
from datetime import date, datetime
from typing import Any, Dict
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

from app.services.docs_gen.one_time_contract import OneTimeContractData


class OneTimeContractStateData:
    def __init__(self, state: FSMContext) -> None:
        self.state = state

    async def init(self):
        data = {
            "date": None,
            "client_name": None,
            "address": None,
            "contract_number_cpm": None,
            "ac_maintenance_price": None,
            "ac_repair_price": None,
            "other_price": None,
            "discount_price": None,
        }
        await self.set_one_time_contract(data)

    async def get_one_time_contract(self) -> dict:
        data = await self.state.get_data()
        return data["one_time_contract"]

    async def set_one_time_contract(self, data: dict) -> None:
        await self.state.update_data(one_time_contract=data)

    async def update_one_time_contract(self, **kwargs):
        data = await self.get_one_time_contract()
        data.update(**kwargs)
        await self.set_one_time_contract(data)

    async def get_one_time_contract_key_value(self, key: Any) -> Any:
        data = await self.get_one_time_contract()
        return data[key]

    async def set_date(self, date: date) -> None:
        await self.update_one_time_contract(date=date.strftime("%d.%m.%Y"))

    async def get_date(self) -> date:
        state_date = await self.get_one_time_contract_key_value("date")
        return datetime.strptime(state_date, "%d.%m.%Y").date()

    async def set_address(self, address: str) -> None:
        await self.update_one_time_contract(address=address)

    async def get_address(self) -> str:
        return await self.get_one_time_contract_key_value("address")

    async def set_client_name(self, client_name: str) -> None:
        await self.update_one_time_contract(client_name=client_name)

    async def get_client_name(self) -> str:
        return await self.get_one_time_contract_key_value("client_name")

    async def set_contract_number_cpm(self, contract_number_cpm: str) -> None:
        await self.update_one_time_contract(contract_number_cpm=contract_number_cpm)

    async def get_contract_number_cpm(self) -> str:
        return await self.get_one_time_contract_key_value("contract_number_cpm")

    async def set_ac_maintenance_price(self, ac_maintenance_price: float) -> None:
        await self.update_one_time_contract(ac_maintenance_price=ac_maintenance_price)

    async def get_ac_maintenance_price(self) -> float:
        return await self.get_one_time_contract_key_value("ac_maintenance_price")

    async def set_ac_repair_price(self, ac_repair_price: float) -> None:
        await self.update_one_time_contract(ac_repair_price=ac_repair_price)

    async def get_ac_repair_price(self) -> float:
        return await self.get_one_time_contract_key_value("ac_repair_price")

    async def set_other_price(self, other_price: float) -> None:
        await self.update_one_time_contract(other_price=other_price)

    async def get_other_price(self) -> float:
        return await self.get_one_time_contract_key_value("other_price")

    async def set_discount_price(self, discount_price: float) -> None:
        await self.update_one_time_contract(discount_price=discount_price)

    async def get_discount_price(self) -> float:
        return await self.get_one_time_contract_key_value("discount_price")

    async def get_one_time_contract_data(self) -> OneTimeContractData:
        return OneTimeContractData(
            contract_number_cpm=await self.get_contract_number_cpm(),
            _date=await self.get_date(),
            client_name=await self.get_client_name(),
            address=await self.get_address(),
            ac_maintenance_price=await self.get_ac_maintenance_price(),
            ac_repair_price=await self.get_ac_repair_price(),
            other_price=await self.get_other_price(),
            discount_price=await self.get_discount_price(),
        )


class OneTimeContractMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["one_time_contract"] = OneTimeContractStateData(data["state"])
        return await handler(event, data)
