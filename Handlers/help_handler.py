from mailbox import Message

from aiogram import Router
from aiogram.filters import Command

from Models.user_model import User

router = Router()

@router.message(Command("help"))
async def help_command(message: Message, actor: User):
    user_help = """
    /menu - чтоб вызвать меню
    /new_ticket - чтоб создать задачу
    /ticket {действие} {номер}
    /help - список команд
    """
    admin_help = """
    /menu - чтоб вызвать меню
    /new_ticket - чтоб создать задачу
    /ticket {действие} {номер}
    /help - список команд
    /users - список всех пользователей
    /ban_user {tg_id} - удалить пользователя
    """

    if actor.role == actor.role.user:
        await message.answer(user_help)
    else:
        await message.answer(admin_help)