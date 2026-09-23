from aiogram import Router
from aiogram.filters import Command

router = Router()

@router.message(Command("admin_menu"))
async def admin_menu_command(message, actor, session):
    await message.answer("admin menu")