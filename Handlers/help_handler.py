from mailbox import Message

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import reply_markup_union

from Models.user_model import User
from Service.keyboard_service import get_main_menu_keyboard

router = Router()

@router.message(
    F.chat.type == "private",
    Command("help")
)
async def help_command(message: Message, actor: User):
    user_help = """
    /menu - чтоб вызвать меню
    /ticket {действие} {номер}
    /tickets - список моих заявок
    /help - список команд
    """
    admin_help = """
    /menu - чтоб вызвать меню
    /ticket {действие} {номер}
    /tickets - список заявок
    /help - список команд
    /users - список всех пользователей
    /ban_user {tg_id} - удалить пользователя
    """

    if actor.role == actor.role.user:
        await message.answer(user_help)
    else:
        await message.answer(admin_help)

@router.message(
    F.chat.type == "private",
    Command("menu"))
async def menu_command(message:Message, actor: User):
    await message.answer(
        "Меню:",
        reply_markup=get_main_menu_keyboard(actor)
    )