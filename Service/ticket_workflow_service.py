import os

from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from Enums.notification_kind_enum import NotificationKind
from Enums.role_enum import Role
from Models.ticket_model import Ticket
from Models.user_model import User
from Repositories import user_repository, ticket_notification_repository
from Service import ticket_service, ticket_notification_service, user_service


async def close_ticket(
        bot: Bot,
        session: Session,
        actor: User,
        ticket_id: int
):
    ticket = ticket_service.close_ticket(
        session=session,
        actor=actor,
        ticket_id=ticket_id
    )

    text = (
        f"🆕 Заявка #{ticket.id}\n"
        f"Тема: {ticket.title}\n\n"
        f"{ticket.description}\n\n"
        f"Статус: ✅ Закрыта (закрыл: {actor.full_name})"
    )

    notifications = await ticket_notification_service.edit_all_notifications(
        bot=bot,
        session=session,
        ticket=ticket,
        new_text=text
    )

    await ticket_notification_service.notify_author(
        bot=bot,
        notifications=notifications,
        text=f"Ваша заявка #{ticket.id} закрыта"
    )

    return ticket


async def take_ticket(
        bot: Bot,
        session: Session,
        actor: User,
        ticket_id: int
):
    ticket = ticket_service.take_ticket_in_progress(
        session=session,
        actor=actor,
        ticket_id=ticket_id
    )

    text = (
        f"🆕 Заявка #{ticket.id}\n"
        f"Тема: {ticket.title}\n\n"
        f"{ticket.description}\n\n"
        f"Статус: 🔵 В работе (взял: {actor.full_name})"
    )

    close_keyboard = InlineKeyboardBuilder()
    close_keyboard.button(
        text="✅ Закрыть заявку",
        callback_data=f"ticket:complete:{ticket.id}:1"
    )

    notifications = await ticket_notification_service.edit_all_notifications(
        bot=bot,
        session=session,
        ticket=ticket,
        new_text=text,
        keyboard_for={
            actor.telegram_id: close_keyboard.as_markup()
        }
    )

    await ticket_notification_service.notify_author(
        bot=bot,
        notifications=notifications,
        text=f"{actor.full_name} взял вашу заявку #{ticket.id} в работу"
    )

    return ticket


async def cancel_ticket(
        bot: Bot,
        session: Session,
        actor: User,
        ticket_id: int
):
    ticket = ticket_service.cancel_ticket(
        session=session,
        actor=actor,
        ticket_id=ticket_id
    )

    text = (
        f"🆕 Заявка #{ticket.id}\n"
        f"Тема: {ticket.title}\n\n"
        f"{ticket.description}\n\n"
        f"Статус: ❌ Отменена автором"
    )

    await ticket_notification_service.edit_all_notifications(
        bot=bot,
        session=session,
        ticket=ticket,
        new_text=text
    )

    return ticket


async def create_ticket_and_notify(
        bot: Bot,
        session: Session,
        actor: User,
        title: str,
        description: str,
        photo_id: str | None
):
    ticket = ticket_service.create_ticket(
        session=session,
        description=description,
        user_id=actor.id,
        title=title,
        photo_id=photo_id
    )

    text = (
        f"🆕 Заявка #{ticket.id}\n"
        f"От: {actor.full_name} (каб. {actor.cabinet})\n"
        f"Тема: {ticket.title}\n\n"
        f"{ticket.description}\n\n"
        f"Статус: 🟡 Открыт"
    )

    async def send_ticket_notification(
            chat_id: int,
            keyboard=None
    ):
        if ticket.photo_id:
            return await bot.send_photo(
                chat_id=chat_id,
                photo=ticket.photo_id,
                caption=text,
                reply_markup=keyboard
            )

        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard
        )

    # Автор
    author_keyboard = InlineKeyboardBuilder()
    author_keyboard.button(
        text="Отменить заявку",
        callback_data=f"ticket:cancel:{ticket.id}:1"
    )

    sent = await send_ticket_notification(
        actor.telegram_id,
        keyboard=author_keyboard.as_markup()
    )

    ticket_notification_repository.create_notification(
        session=session,
        ticket_id=ticket.id,
        chat_id=sent.chat.id,
        message_id=sent.message_id,
        kind=NotificationKind.author
    )

    # Группа
    group_chat_id = os.getenv("GROUP_CHAT_ID")

    if group_chat_id:
        sent = await send_ticket_notification(
            int(group_chat_id)
        )

        ticket_notification_repository.create_notification(
            session=session,
            ticket_id=ticket.id,
            chat_id=sent.chat.id,
            message_id=sent.message_id,
            kind=NotificationKind.group
        )

    # Администраторы
    admin_keyboard = InlineKeyboardBuilder()
    admin_keyboard.button(
        text="✅ Взять в работу",
        callback_data=f"ticket:select:{ticket.id}:{1}"
    )

    admins = user_repository.find_users_by_role(
        session=session,
        role=Role.admin
    )

    for admin in admins:
        sent = await send_ticket_notification(
            admin.telegram_id,
            keyboard=admin_keyboard.as_markup()
        )

        ticket_notification_repository.create_notification(
            session=session,
            ticket_id=ticket.id,
            chat_id=sent.chat.id,
            message_id=sent.message_id,
            kind=NotificationKind.admin
        )

    return ticket
async def complete_ticket(
        bot: Bot,
        session: Session,
        actor: User,
        ticket_id: int
):
    ticket = ticket_service.complete_ticket(
        session=session,
        actor=actor,
        ticket_id=ticket_id
    )


    text = (
        f"🆕 Заявка #{ticket.id}\n"
        f"Тема: {ticket.title}\n\n"
        f"{ticket.description}\n\n"
        f"Статус: ✅ Завершена\n"
        f"Взял: {ticket.assigned_admin.full_name}\n"
        f"Завершил: {actor.full_name}"
    )

    notifications = await ticket_notification_service.edit_all_notifications(
        bot=bot,
        session=session,
        ticket=ticket,
        new_text=text
    )

    await ticket_notification_service.notify_author(
        bot=bot,
        notifications=notifications,
        text=f"Ваша заявка #{ticket.id} завершена"
    )

    return ticket