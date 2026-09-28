from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from Enums.status_enum import Status
from Exceptions.AccessDeniedError import AccessDeniedError
from Exceptions.TicketValidationError import TicketValidationError
from Handlers.ticket_handler import show_tickets_page, start_ticket_creation
from Keyboards.tickets_list_keyboard import ticket_keyboard
from Models.user_model import User
from Service import ticket_workflow_service
from Service import ticket_service, access_control

TICKETS_PER_PAGE = 10

router = Router()

@router.callback_query(F.data == "ticket:create")
async def create_ticket_callback(
        callback: CallbackQuery,
        actor: User,
        state: FSMContext
):
    await start_ticket_creation(
        callback.message,
        actor,
        state
    )
    await callback.answer()

@router.callback_query(F.data.startswith("ticket:select:"))
async def take_ticket_handler(
        callback: CallbackQuery,
        actor: User,
        session: Session,
        bot: Bot
):
    print("TAKE HANDLER", callback.data)
    parts = callback.data.split(":")
    ticket_id = int(parts[2])

    try:
        await ticket_workflow_service.take_ticket(
            bot=bot,
            session=session,
            actor=actor,
            ticket_id=ticket_id
        )
    except AccessDeniedError as e:
        await callback.answer(str(e), show_alert=True)
        return
    except TicketValidationError as e:
        await callback.answer(str(e), show_alert=True)
        return

    await callback.answer("Взял в работу!")


@router.callback_query(F.data.startswith("ticket:cancel:"))
async def cancel_ticket_handler(
        callback: CallbackQuery,
        actor: User,
        session: Session,
        bot: Bot
):
    parts = callback.data.split(":")
    ticket_id = int(parts[2])

    try:
        await ticket_workflow_service.cancel_ticket(
            bot=bot,
            session=session,
            actor=actor,
            ticket_id=ticket_id
        )
    except AccessDeniedError as e:
        await callback.answer(str(e), show_alert=True)
        return
    except TicketValidationError as e:
        await callback.answer(str(e), show_alert=True)
        return

    await callback.answer("Заявка отменена")

@router.callback_query(F.data.startswith("ticket:complete:"))
async def complete_ticket_handler(
        callback: CallbackQuery,
        actor: User,
        session: Session,
        bot: Bot
):
    parts = callback.data.split(":")
    ticket_id = int(parts[2])

    try:
        await ticket_workflow_service.complete_ticket(
            bot=bot,
            session=session,
            actor=actor,
            ticket_id=ticket_id
        )
    except AccessDeniedError as e:
        await callback.answer(str(e), show_alert=True)
        return
    except TicketValidationError as e:
        await callback.answer(str(e), show_alert=True)
        return

    await callback.answer("Заявка завершена")



@router.callback_query(F.data.startswith("tickets:page:"))
async def tickets_page_handler(
        callback: CallbackQuery,
        actor: User,
        session: Session
):
    page = int(callback.data.split(":")[2])

    if actor is None:
        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True
        )
        return

    await show_tickets_page(
        message=callback.message,
        actor=actor,
        session=session,
        page=page
    )

    await callback.answer()


@router.callback_query(F.data == "tickets:noop")
async def tickets_noop_handler(
        callback: CallbackQuery
):
    await callback.answer()


@router.callback_query(F.data.regexp(r"^ticket:\d+:\d+$"))
async def ticket_info_handler(
        callback: CallbackQuery,
        actor: User,
        session: Session
):
    parts = callback.data.split(":")

    ticket_id = int(parts[1])
    page = int(parts[2])

    if actor is None:
        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True,
        )
        return
    ticket = ticket_service.get_ticket_by_id(
        session=session,
        ticket_id=ticket_id)

    if ticket is None:
        await callback.answer(
            "Заявка не найдена",
            show_alert=True
        )
        return

    try:
        access_control.ensure_can_view_ticket(
            actor=actor,
            ticket=ticket
        )
    except AccessDeniedError:
        await callback.answer(
            "Доступен просмотр только своих заявок",
            show_alert=True
        )
        return
    assigned_name = (
        ticket.assigned_admin.full_name
        if ticket.assigned_admin
        else "Не назначен"
    )

    completed_name = (
        ticket.completed_by_admin.full_name
        if ticket.completed_by_admin
        else "Не завершён"
    )

    if ticket.status == Status.open:
        status = "🟢 Открыт"
    elif ticket.status == Status.in_progress:
        status = "🔵 В процессе"
    else:
        status = "🔴 Закрыт"

    caption = f"""
    Заявка

    ID: {ticket.id}
    Создатель: {ticket.author.full_name}
    Кабинет: {ticket.author.cabinet}
    Тема: {ticket.title}
    Описание: {ticket.description}
    Статус: {status}
    Взял: {assigned_name}
    Завершил: {completed_name}
    """
    await callback.message.edit_text(
        text=caption,
        reply_markup=ticket_keyboard(
            ticket=ticket,
            actor=actor,
            page=page
        )
    )

    await callback.answer()

@router.callback_query(F.data == "ticket:photo_back")
async def ticket_photo_back_handler(
        callback: CallbackQuery
):
    await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data.startswith("ticket:photo:"))
async def ticket_show_photo(
        callback: CallbackQuery,
        actor: User,
        session: Session
):

    try:
        ticket_id = int(callback.data.split(":")[2])
    except ValueError:
        await callback.answer("Ticket id must be int", show_alert=True)
        return
    try:
        ticket = ticket_service.get_ticket_by_id(
            session=session,
            ticket_id=ticket_id
        )
        if ticket is None:
            await callback.answer("Ticket has not been found!", show_alert=True)
            return
        access_control.ensure_can_view_ticket(
            actor=actor,
            ticket=ticket
        )
    except TicketValidationError as e:
        await callback.answer(str(e), show_alert=True)
        return
    except AccessDeniedError as e:
        await callback.answer(str(e), show_alert=True)
        return


    if ticket.photo_id is None:
        await callback.answer("The ticket has no photo", show_alert=True)
        return
    photo_keyboard = InlineKeyboardBuilder()

    photo_keyboard.button(
        text="⬅️ Назад",
        callback_data="ticket:photo_back"
    )

    await callback.message.answer_photo(
        photo=ticket.photo_id,
        reply_markup=photo_keyboard.as_markup()
    )
    await callback.answer()

