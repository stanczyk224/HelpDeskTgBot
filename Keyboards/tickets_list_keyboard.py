from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from  Enums.role_enum import Role
from Enums.status_enum import Status
from Models.ticket_model import Ticket
from Models.user_model import User


def tickets_list_keyboard(
    tickets,
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    for ticket in tickets:
        title = f"{ticket.title}".strip()

        builder.row(
            InlineKeyboardButton(
                text=f"{ticket.id}) {title}",
                callback_data=f"ticket:{ticket.id}:{page}"
            )
        )

    navigation = []

    if page > 1:
        navigation.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"tickets:page:{page - 1}"
            )
        )

    navigation.append(
        InlineKeyboardButton(
            text=f"{page}/{total_pages}",
            callback_data="tickets:noop"
        )
    )

    if page < total_pages:
        navigation.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"tickets:page:{page + 1}",
            )
        )

    builder.row(*navigation)

    return builder.as_markup()

def ticket_keyboard(
        ticket: Ticket,
        actor: User,
        page: int
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    if ticket.status == Status.open and ticket.user_id == actor.id:
        builder.button(
            text="Отменить заявку",
            callback_data=f"ticket:cancel:{ticket.id}:{page}"
        )
    elif ticket.status == Status.open and actor.role == Role.admin:
        builder.button(
            text="Взять в работу",
            callback_data=f"ticket:select:{ticket.id}:{page}"
        )
    else:
        pass
    if ticket.status == Status.in_progress and actor.role == Role.admin:
        builder.button(
            text="Завершить заявку",
            callback_data=f"ticket:complete:{ticket.id}:{page}"
        )
    if ticket.photo_id is not None:
        builder.button(
            text="📸 показать фото",
            callback_data=f"ticket:photo:{ticket.id}"
        )

    builder.button(
        text="⬅️ в меню",
        callback_data=f"tickets:page:{page}"
    )



    builder.adjust(1)

    return builder.as_markup()


