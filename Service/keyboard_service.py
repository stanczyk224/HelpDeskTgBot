from Models.user_model import User
from Enums.role_enum import Role

from aiogram.types import InlineKeyboardMarkup

from Keyboards.main_menu_keyboards import main_menu_keyboard_user, main_menu_keyboard_admin

def get_main_menu_keyboard(user: User) -> InlineKeyboardMarkup:
    if user.role == Role.admin:
        return main_menu_keyboard_admin()

    return main_menu_keyboard_user()

