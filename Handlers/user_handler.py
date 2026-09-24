
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.orm import Session

from Repositories import user_repository

router = Router()

@router.message(Command("all_tickets"))
async def all_tickets_handler(
        message: Message,
        session: Session
):
    actor_tg_id = message.from_user.id
    actor = user_repository.find_user_by_telegram_id(session=session,telegram_id=actor_tg_id)

    if actor is None:
        await message.answer("Пользователь не найден")
        return

