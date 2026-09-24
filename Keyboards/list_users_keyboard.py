from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Enums.role_enum import Role


def users_list_keyboard(
    users,
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    for user in users:
        name = f"{user.full_name}".strip()

        builder.row(
            InlineKeyboardButton(
                text=f"{user.id}) {name}",
                callback_data=f"user:{user.id}:{page}",
            )
        )

    navigation = []

    if page > 1:
        navigation.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"users:page:{page - 1}",
            )
        )

    navigation.append(
        InlineKeyboardButton(
            text=f"{page}/{total_pages}",
            callback_data="users:noop",
        )
    )

    if page < total_pages:
        navigation.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"users:page:{page + 1}",
            )
        )

    builder.row(*navigation)

    return builder.as_markup()


def user_keyboard(
    user,
    page: int,
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    if user.role == Role.admin:
        builder.button(
            text="⬇️ Понизить",
            callback_data=f"user:demote:{user.id}:{page}",
        )
    else:
        builder.button(
            text="⬆️ Повысить",
            callback_data=f"user:promote:{user.id}:{page}",
        )

    builder.button(
        text="🗑 Удалить",
        callback_data=f"user:delete:{user.id}:{page}",
    )

    builder.button(
        text="⬅️ Назад",
        callback_data=f"users:page:{page}",
    )

    builder.adjust(1)

    return builder.as_markup()

