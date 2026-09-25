from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.orm import Session

from Enums.notification_kind_enum import NotificationKind
from Models.ticket_model import Ticket
from Repositories import ticket_notification_repository


async def edit_all_notifications(
        bot: Bot,
        session: Session,
        ticket: Ticket,
        new_text: str,
        keyboard_for: dict[int, InlineKeyboardMarkup] | None = None
):
    notifications = ticket_notification_repository.find_by_ticket_id(
        session=session,
        ticket_id=ticket.id
    )

    for notification in notifications:
        keyboard = None

        if keyboard_for and notification.chat_id in keyboard_for:
            keyboard = keyboard_for[notification.chat_id]

        try:
            if ticket.photo_id:
                await bot.edit_message_caption(
                    chat_id=notification.chat_id,
                    message_id=notification.message_id,
                    caption=new_text,
                    reply_markup=keyboard
                )
            else:
                await bot.edit_message_text(
                    chat_id=notification.chat_id,
                    message_id=notification.message_id,
                    text=new_text,
                    reply_markup=keyboard
                )
        except Exception as e:
            print(f"Ошибка обновления notification: {e} {notification.chat_id} {notification.message_id}")
            continue

    return notifications


async def notify_author(
        bot: Bot,
        notifications,
        text: str
):
    for notification in notifications:
        if notification.kind == NotificationKind.author:
            await bot.send_message(
                chat_id=notification.chat_id,
                text=text
            )