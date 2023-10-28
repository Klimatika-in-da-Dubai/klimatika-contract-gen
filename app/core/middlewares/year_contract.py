from collections.abc import Awaitable, Callable
from datetime import date, datetime
from typing import Any, Dict, Literal
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

from app.services.docs_gen.year_contract import YearContractData


class YearContractStateData:
    def __init__(self, state: FSMContext):
        self.state = state

    async def init(self):
        data = {
            "date": "1.1.1",
            "address": "empty_address!!!",
            "client_name": "empty_client_name!!!!",
            "contract_number_cpm": "empty_contract_number!!!",
            "service1_date": "1.1.1",
            "service1_price": 0,
            "discount": 0,
            "service_count": 2,
        }
        await self.set_year_contract(data)

    async def get_year_contract(self) -> dict:
        data = await self.state.get_data()
        return data["year_contract"]

    async def set_year_contract(self, data: dict) -> None:
        await self.state.update_data(year_contract=data)

    async def update_year_contract(self, **kwargs):
        data = await self.get_year_contract()
        data.update(**kwargs)
        await self.set_year_contract(data)

    async def get_year_contract_key_value(self, key: Any) -> Any:
        data = await self.get_year_contract()
        return data[key]

    async def set_date(self, date: date) -> None:
        await self.update_year_contract(date=date.strftime("%d.%m.%Y"))

    async def get_date(self) -> date:
        state_date = await self.get_year_contract_key_value("date")
        return datetime.strptime(state_date, "%d.%m.%Y").date()

    async def set_address(self, address: str) -> None:
        await self.update_year_contract(address=address)

    async def get_address(self) -> str:
        return await self.get_year_contract_key_value("address")

    async def set_client_name(self, client_name: str) -> None:
        await self.update_year_contract(client_name=client_name)

    async def get_client_name(self) -> str:
        return await self.get_year_contract_key_value("client_name")

    async def set_contract_number_cpm(self, contract_number_cpm: str) -> None:
        await self.update_year_contract(contract_number_cpm=contract_number_cpm)

    async def get_contract_number_cpm(self) -> str:
        return await self.get_year_contract_key_value("contract_number_cpm")

    async def set_service1_date(self, date: date) -> None:
        await self.update_year_contract(service1_date=date.strftime("%d.%m.%Y"))

    async def get_service1_date(self) -> date:
        service1_date = await self.get_year_contract_key_value("service1_date")
        return datetime.strptime(service1_date, "%d.%m.%Y").date()

    async def set_service1_price(self, price: float) -> None:
        await self.update_year_contract(service1_price=price)

    async def get_service1_price(self) -> float:
        return await self.get_year_contract_key_value("service1_price")

    async def set_discount(self, discount: float) -> None:
        await self.update_year_contract(discount=discount)

    async def get_discount(self) -> float:
        return await self.get_year_contract_key_value("discount")

    async def set_service_count(self, count: Literal[2, 3]) -> None:
        await self.update_year_contract(service_count=count)

    async def get_service_count(self) -> Literal[2, 3]:
        return await self.get_year_contract_key_value("service_count")

    async def get_year_contract_data(self) -> YearContractData:
        return YearContractData(
            contract_number_cpm=await self.get_contract_number_cpm(),
            _date=await self.get_date(),
            client_name=await self.get_client_name(),
            address=await self.get_address(),
            service_count=await self.get_service_count(),
            _service1_date=await self.get_service1_date(),
            service1_price=await self.get_service1_price(),
            discount=await self.get_discount(),
        )


class YearContractMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["year_contract"] = YearContractStateData(data["state"])
        return await handler(event, data)
