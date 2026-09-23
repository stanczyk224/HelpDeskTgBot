from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import os
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Enums.notification_kind_enum import NotificationKind
from Enums.role_enum import Role
from Repositories import user_repository, ticket_repository, ticket_notification_repository
from Exceptions.TicketValidationError import TicketValidationError
from Service import ticket_service
from States.CreateTicketState import CreateTicketStates
from Utils.telegram_helpers import require_text

router = Router()

@router.message(Command("new_ticket"))
async def new_ticket_handler(message: Message, actor, state: FSMContext):
    if actor is None:
        await message.answer("Сначала нужно зарегистрироваться — напиши /start")
        return

    await message.answer("Опиши тему заявки одной строкой")
    await state.set_state(CreateTicketStates.waiting_for_title)

@router.message(CreateTicketStates.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    text = await require_text(message)
    if text is None:
        return
    await state.update_data(title=text)
    await message.answer("Опиши проблему подробнее")
    await state.set_state(CreateTicketStates.waiting_for_description)


@router.message(CreateTicketStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    text = await require_text(message)
    if text is None:
        return
    await state.update_data(description=text)
    await message.answer("Прикрепи фото (или напиши «-», если фото нет)")
    await state.set_state(CreateTicketStates.waiting_for_photo)


@router.message(CreateTicketStates.waiting_for_photo)
async def process_photo(message: Message, state: FSMContext, actor, session, bot: Bot):
    photo_id = None
    if message.photo is not None:
        photo_id = message.photo[-1].file_id
    elif message.text != "-":
        await message.answer("Пришли фото или напиши «-», если фото нет")
        return

    data = await state.get_data()

    try:
        ticket = ticket_service.create_ticket(
            session,
            description=data["description"],
            user_id=actor.id,
            title=data["title"],
            photo_id=photo_id
        )
    except TicketValidationError as e:
        await message.answer(f"Ошибка: {e}\n\nПопробуй ещё раз. Опиши тему заявки одной строкой")
        await state.set_state(CreateTicketStates.waiting_for_title)
        return

    await state.clear()

    text = (
        f"🆕 Заявка #{ticket.id}\n"
        f"От: {actor.full_name} (каб. {actor.cabinet})\n"
        f"Тема: {ticket.title}\n\n"
        f"{ticket.description}\n\n"
        f"Статус: 🟡 Открыт"
    )

    async def send_ticket_notification(chat_id: int, keyboard=None):
        if ticket.photo_id:
            return await bot.send_photo(
                chat_id=chat_id,
                photo=ticket.photo_id,
                caption=text,
                reply_markup=keyboard
            )
        else:
            return await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard
            )

    author_keyboard = InlineKeyboardBuilder()
    author_keyboard.button(text="Отменить заявку", callback_data=f"cancel_ticket:{ticket.id}")
    sent = await send_ticket_notification(message.chat.id, keyboard=author_keyboard.as_markup())
    ticket_notification_repository.create_notification(
        session, ticket_id=ticket.id, chat_id=sent.chat.id, message_id=sent.message_id, kind=NotificationKind.author
    )

    group_chat_id = os.getenv("GROUP_CHAT_ID")
    if group_chat_id:
        sent = await send_ticket_notification(int(group_chat_id))
        ticket_notification_repository.create_notification(
            session, ticket_id=ticket.id, chat_id=sent.chat.id, message_id=sent.message_id, kind=NotificationKind.group
        )

    admin_keyboard = InlineKeyboardBuilder()
    admin_keyboard.button(text="✅ Взять в работу", callback_data=f"take_ticket:{ticket.id}")
    admins = user_repository.find_users_by_role(session, role=Role.admin)
    for admin in admins:
        sent = await send_ticket_notification(admin.telegram_id, keyboard=admin_keyboard.as_markup())
        ticket_notification_repository.create_notification(
            session, ticket_id=ticket.id, chat_id=sent.chat.id, message_id=sent.message_id, kind=NotificationKind.admin
        )