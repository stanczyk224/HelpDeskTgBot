from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Awaitable, Any

from db import SessionLocal
from Repositories import user_repository
class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        if not hasattr(event, "from_user") or event.from_user is None:
            return await handler(event, data)

        telegram_id = event.from_user.id
        with SessionLocal() as session:
            actor = user_repository.find_user_by_telegram_id(session, telegram_id)
            data["actor"] = actor
            data["session"] = session
            return await handler(event, data)

