import asyncio
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from db import Base, engine
from Middlewares.user_middleware import UserMiddleware
from Handlers import main_router
from Jobs.cleanup import cleanup_old_tickets_loop


async def main():
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set in .env")

    Base.metadata.create_all(engine)

    bot = Bot(token=bot_token)
    dp = Dispatcher()

    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    dp.include_router(main_router)

    asyncio.create_task(cleanup_old_tickets_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())