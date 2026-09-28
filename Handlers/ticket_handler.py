from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import os
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from Enums.notification_kind_enum import NotificationKind
from Enums.role_enum import Role
from Exceptions.AccessDeniedError import AccessDeniedError
from Keyboards.tickets_list_keyboard import tickets_list_keyboard
from Models.user_model import User
from Repositories import user_repository, ticket_repository, ticket_notification_repository
from Exceptions.TicketValidationError import TicketValidationError
from Service import ticket_service, ticket_workflow_service
from Service.access_control import ensure_is_admin, ensure_is_ticket_author
from States.CreateTicketState import CreateTicketStates
from Utils.telegram_helpers import require_text

router = Router()

TICKETS_PER_PAGE = 10

async def start_ticket_creation(
        message: Message,
        actor: User,
        state: FSMContext
):
    if actor is None:
        await message.answer("Сначала нужно зарегистрироваться — напиши /start")
        return

    await message.answer("Опиши тему заявки одной строкой")
    await state.set_state(CreateTicketStates.waiting_for_title)


async def show_tickets_page(
        message: Message,
        actor: User,
        session: Session,
        page: int
):
    tickets, total_tickets = ticket_service.get_tickets_page(
        session=session,
        actor=actor,
        page=page,
        per_page=TICKETS_PER_PAGE
    )

    total_pages = max(
        1,
        (total_tickets + TICKETS_PER_PAGE - 1) // TICKETS_PER_PAGE
    )

    if page > total_pages:
        page = total_pages

        tickets, total_tickets = ticket_service.get_tickets_page(
            session=session,
            actor=actor,
            page=page,
            per_page=TICKETS_PER_PAGE
        )

    await message.edit_text(
        "Список заявок:",
        reply_markup=tickets_list_keyboard(
            tickets=tickets,
            page=page,
            total_pages=total_pages
        )
    )

@router.message(Command("ticket"))
async def ticket_command(
        message: Message,
        actor: User,
        command: CommandObject,
        session: Session,
        bot: Bot,
        state: FSMContext
):
    if actor is None:
        await message.answer("Пользователь не найден")
        return

    if not command.args:
        await message.answer(
            "Использование:\n"
            "/ticket create\n"
            "/ticket take ID\n"
            "/ticket complete ID\n"
            "/ticket close ID\n"
            "/ticket cancel ID"
        )
        return

    parts = command.args.split()
    action = parts[0].lower()

    # Создание заявки
    if action == "create":
        if len(parts) != 1:
            await message.answer("Использование: /ticket create")
            return

        await start_ticket_creation(
            message=message,
            actor=actor,
            state=state
        )
        return

    # Все остальные команды требуют ID
    if len(parts) != 2:
        await message.answer(
            "Использование: /ticket <action> <ID>"
        )
        return

    try:
        ticket_id = int(parts[1])
    except ValueError:
        await message.answer("ID тикета должен быть числом")
        return

    try:
        if action == "take":
            await ticket_workflow_service.take_ticket(
                bot=bot,
                session=session,
                actor=actor,
                ticket_id=ticket_id
            )

        elif action == "complete":
            await ticket_workflow_service.complete_ticket(
                bot=bot,
                session=session,
                actor=actor,
                ticket_id=ticket_id
            )

        elif action == "close":
            await ticket_workflow_service.close_ticket(
                bot=bot,
                session=session,
                actor=actor,
                ticket_id=ticket_id
            )

        elif action == "cancel":
            await ticket_workflow_service.cancel_ticket(
                bot=bot,
                session=session,
                actor=actor,
                ticket_id=ticket_id
            )

        else:
            await message.answer(
                f"Неизвестное действие: {action}\n"
                "Доступно: create, take, complete, close, cancel"
            )
            return

    except AccessDeniedError as e:
        await message.answer(str(e))
        return

    except TicketValidationError as e:
        await message.answer(str(e))
        return

    await message.answer(
        f"Операция `{action}` для тикета #{ticket_id} выполнена",
        parse_mode="Markdown"
    )



@router.message(Command("tickets"))
async def all_tickets_handler(
        message: Message,
        actor: User,
        session: Session
):

    if actor is None:
        await message.answer("Пользователь не найден")
        return

    tickets, total_tickets = ticket_service.get_tickets_page(
        session=session,
        actor=actor,
        page=1,
        per_page=TICKETS_PER_PAGE
    )

    total_pages = max(
        1,
        (total_tickets + TICKETS_PER_PAGE - 1) // TICKETS_PER_PAGE
    )

    await message.answer(
        "Список заявок:",
        reply_markup=tickets_list_keyboard(
            tickets=tickets,
            page=1,
            total_pages=total_pages
        )
    )

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
    admin_keyboard.button(text="✅ Взять в работу", callback_data=f"ticket:select:{ticket.id}")
    admins = user_repository.find_users_by_role(session, role=Role.admin)
    for admin in admins:
        sent = await send_ticket_notification(admin.telegram_id, keyboard=admin_keyboard.as_markup())
        ticket_notification_repository.create_notification(
            session, ticket_id=ticket.id, chat_id=sent.chat.id, message_id=sent.message_id, kind=NotificationKind.admin
        )

