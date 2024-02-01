import asyncio
from datetime import datetime
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from app.settings.config import load_config
from app.core.handlers import main_router

logging.basicConfig(
    format=(
        "%(asctime)s - [%(levelname)s] - %(name)s"
        "- (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
    ),
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f"logs/{datetime.now().date()}.log"),
        logging.StreamHandler(),
    ],
)


def setup_routers(dp: Dispatcher):
    dp.include_routers(main_router)


async def main():
    config = load_config()
    bot = Bot(config.bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=RedisStorage.from_url(config.redis.url))

    setup_routers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()


if __name__ == "__main__":
    asyncio.run(main())
