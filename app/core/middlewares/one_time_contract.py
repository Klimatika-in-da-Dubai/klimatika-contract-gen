from collections.abc import Awaitable, Callable
from datetime import date, datetime
from enum import StrEnum
from typing import Any, Dict
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

from app.services.docs_gen.one_time_contract import OneTimeContractData, ServiceData


class OneTimeContractService(StrEnum):
    AC_MAINTENANCE = "ac_maintenance"
    AC_REPAIR = "ac_repair"
    OTHER = "other"


SERVICES_ORDER = {
    OneTimeContractService.AC_MAINTENANCE: 0,
    OneTimeContractService.AC_REPAIR: 1,
    OneTimeContractService.OTHER: 2,
}

SERVICES_NAME = {
    OneTimeContractService.AC_MAINTENANCE: "Premium AC Maintenance",
    OneTimeContractService.AC_REPAIR: "Premium AC Repairs",
    OneTimeContractService.OTHER: "Other",
}

SERVICES_RU_NAME = {
    OneTimeContractService.AC_MAINTENANCE: "обслуживание кондиционера",
    OneTimeContractService.AC_REPAIR: "ремонт кондиционера",
    OneTimeContractService.OTHER: "другое",
}


class OneTimeContractStateData:
    def __init__(self, state: FSMContext) -> None:
        self.state = state

    async def init(self):
        data = {
            "date": None,
            "client_name": None,
            "address": None,
            "contract_number_cpm": None,
            "services": {
                # "ac_maintenance":  0,
                # "ac_repair":  0,
                # "other_price":  0,
            },
            "discount": None,
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

    async def set_selected_service(self, service: OneTimeContractService):
        await self.update_one_time_contract(selected_service=service)

    async def unselect_service(self):
        await self.update_one_time_contract(selected_service=None)

    async def get_selected_service(self) -> OneTimeContractService:
        return await self.get_one_time_contract_key_value("selected_service")

    async def remove_service(self, service: OneTimeContractService) -> None:
        services = await self.get_services()
        services.pop(service)
        await self.update_services(services)

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

    async def get_services(self) -> dict:
        return await self.get_one_time_contract_key_value("services")

    async def update_services(self, services: dict) -> None:
        return await self.update_one_time_contract(services=services)

    async def is_service_in_services(self, service: OneTimeContractService) -> bool:
        return str(service) in await self.get_services()

    async def get_service_price(self, service: OneTimeContractService) -> float:
        services = await self.get_services()
        return services[str(service)]

    async def set_service_price(self, service: str, price: float) -> None:
        services = await self.get_services()
        services[service] = price
        await self.update_services(services)

    async def set_ac_maintenance_price(self, ac_maintenance_price: float) -> None:
        await self.set_service_price(
            OneTimeContractService.AC_MAINTENANCE, ac_maintenance_price
        )

    async def get_ac_maintenance_price(self) -> float:
        return await self.get_service_price(OneTimeContractService.AC_MAINTENANCE)

    async def set_ac_repair_price(self, ac_repair_price: float) -> None:
        await self.set_service_price(OneTimeContractService.AC_REPAIR, ac_repair_price)

    async def get_ac_repair_price(self) -> float:
        return await self.get_service_price(OneTimeContractService.AC_REPAIR)

    async def set_other_price(self, other_price: float) -> None:
        await self.set_service_price(OneTimeContractService.OTHER, other_price)

    async def get_other_price(self) -> float:
        return await self.get_service_price(OneTimeContractService.OTHER)

    async def set_discount(self, discount: float) -> None:
        await self.update_one_time_contract(discount=discount)

    async def get_discount(self) -> float:
        return await self.get_one_time_contract_key_value("discount")

    async def get_services_data(self) -> list[ServiceData]:
        services = await self.get_services()
        services = sorted(list(services.keys()), key=lambda x: SERVICES_ORDER[x])
        return [
            ServiceData(SERVICES_NAME[service], await self.get_service_price(service))
            for service in services
        ]

    async def get_one_time_contract_data(self) -> OneTimeContractData:
        return OneTimeContractData(
            contract_number_cpm=await self.get_contract_number_cpm(),
            _date=await self.get_date(),
            client_name=await self.get_client_name(),
            address=await self.get_address(),
            services=await self.get_services_data(),
            discount=await self.get_discount(),
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
