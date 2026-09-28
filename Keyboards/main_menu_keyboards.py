from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import InlineKeyboardMarkup


def main_menu_keyboard_user() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    builder.button(
        text="Мои заявки",
        callback_data="tickets:page:1"
    )
    builder.button(
        text="Создать заявку",
        callback_data="ticket:create"
    )

    builder.adjust(1)

    return builder.as_markup()

def main_menu_keyboard_admin() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Заявки",
        callback_data="tickets:page:1"
    )
    builder.button(
        text="Создать заявку",
        callback_data="ticket:create"
    )
    builder.button(
        text="Список пользователей",
        callback_data="users:page:1"
    )

    builder.adjust(1)

    return builder.as_markup()



