import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from db import Base, engine
from Middlewares.user_middleware import UserMiddleware
from Handlers import main_router
from Jobs.cleanup import cleanup_old_tickets_loop

file_handler = logging.FileHandler(
    filename="Logs/bot.log",
    mode="a",
    encoding="utf-8",
    delay=True)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_handler.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        stream_handler,
        file_handler
    ],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", )

async def main():

    logger.debug("Starting bot...")
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

    clean_up_task = asyncio.create_task(cleanup_old_tickets_loop())

    try:
        logger.debug("Bot is ready.")
        await dp.start_polling(bot)
    finally:
        clean_up_task.cancel()
        try:
            await clean_up_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.debug("Bot stopped.")
