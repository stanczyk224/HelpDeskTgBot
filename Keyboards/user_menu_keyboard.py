from aiogram.utils.keyboard import InlineKeyboardBuilder

user_menu = InlineKeyboardBuilder()
user_menu.button(text="Все открытые заявки🟢", callback_data="list_open_tickets_user")
user_menu.button(text="Все закрытые заявки за последние сутки🔴", callback_data="list_closed_tickets_user")

