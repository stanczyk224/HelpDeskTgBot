from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Exceptions.AccessDeniedError import AccessDeniedError
from Exceptions.TicketValidationError import TicketValidationError
from Service import ticket_service
from Repositories import ticket_notification_repository, ticket_repository
from Enums.notification_kind_enum import NotificationKind

router = Router()


async def edit_all_notifications(
    bot: Bot,
    session,
    ticket,
    new_text: str,
    keyboard_for: dict[int, InlineKeyboardMarkup] | None = None
):
    notifications = ticket_notification_repository.find_by_ticket_id(session, ticket_id=ticket.id)
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
        except Exception:
            continue

    return notifications


@router.callback_query(F.data.startswith("take_ticket:"))
async def take_ticket_handler(callback: CallbackQuery, actor, session, bot: Bot):
    ticket_id = int(callback.data.split(":")[1])

    try:
        ticket_service.take_ticket_in_progress(session, actor=actor, ticket_id=ticket_id)
    except AccessDeniedError:
        await callback.answer("У тебя нет прав на это действие", show_alert=True)
        return
    except TicketValidationError as e:
        await callback.answer(str(e), show_alert=True)
        return

    ticket = ticket_repository.find_ticket_by_id(session, ticket_id=ticket_id)

    new_text = (
        f"🆕 Заявка #{ticket.id}\n"
        f"Тема: {ticket.title}\n\n"
        f"{ticket.description}\n\n"
        f"Статус: 🔵 В работе (взял: {actor.full_name})"
    )

    close_keyboard = InlineKeyboardBuilder()
    close_keyboard.button(text="✅ Закрыть заявку", callback_data=f"close_ticket:{ticket.id}")

    notifications = await edit_all_notifications(
        bot, session, ticket, new_text,
        keyboard_for={actor.telegram_id: close_keyboard.as_markup()}
    )

    for notification in notifications:
        if notification.kind == NotificationKind.author:
            await bot.send_message(
                chat_id=notification.chat_id,
                text=f"{actor.full_name} взял вашу заявку #{ticket.id} в работу"
            )

    await callback.answer("Взял в работу!")


@router.callback_query(F.data.startswith("cancel_ticket:"))
async def cancel_ticket_handler(callback: CallbackQuery, actor, session, bot: Bot):
    ticket_id = int(callback.data.split(":")[1])

    try:
        ticket_service.cancel_ticket(session, actor=actor, ticket_id=ticket_id)
    except AccessDeniedError:
        await callback.answer("Это не твоя заявка", show_alert=True)
        return
    except TicketValidationError as e:
        await callback.answer(str(e), show_alert=True)
        return

    ticket = ticket_repository.find_ticket_by_id(session, ticket_id=ticket_id)

    new_text = (
        f"🆕 Заявка #{ticket.id}\n"
        f"Тема: {ticket.title}\n\n"
        f"{ticket.description}\n\n"
        f"Статус: ❌ Отменена автором"
    )

    await edit_all_notifications(bot, session, ticket, new_text)
    await callback.answer("Заявка отменена")


@router.callback_query(F.data.startswith("close_ticket:"))
async def close_ticket_handler(callback: CallbackQuery, actor, session, bot: Bot):
    ticket_id = int(callback.data.split(":")[1])

    try:
        ticket_service.close_ticket(session, actor=actor, ticket_id=ticket_id)
    except AccessDeniedError:
        await callback.answer("У тебя нет прав на это действие", show_alert=True)
        return
    except TicketValidationError as e:
        await callback.answer(str(e), show_alert=True)
        return

    ticket = ticket_repository.find_ticket_by_id(session, ticket_id=ticket_id)

    new_text = (
        f"🆕 Заявка #{ticket.id}\n"
        f"Тема: {ticket.title}\n\n"
        f"{ticket.description}\n\n"
        f"Статус: ✅ Закрыта (закрыл: {actor.full_name})"
    )

    notifications = await edit_all_notifications(bot, session, ticket, new_text)

    for notification in notifications:
        if notification.kind == NotificationKind.author:
            await bot.send_message(
                chat_id=notification.chat_id,
                text=f"Ваша заявка #{ticket.id} закрыта"
            )

    await callback.answer("Заявка закрыта")