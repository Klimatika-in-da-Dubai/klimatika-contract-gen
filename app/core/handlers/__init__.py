from app.core.handlers.main import main_router
from app.core.handlers.one_time_contract.main import one_time_contract_router
from app.core.handlers.year_contract.main import year_contract_router

main_router.include_routers(one_time_contract_router, year_contract_router)
