from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Enums.role_enum import Role
from Exceptions.UserValidationError import UserValidationError
from Service import user_service
from States.RegistrationState import RegistrationStates
from Utils.telegram_helpers import require_text

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, actor, state: FSMContext):
    if actor is not None:
        await message.answer(f"Привет, {actor.full_name}! Ты уже зарегистрирован.")
        await message.answer("""
        /menu - чтоб вызвать меню
        /new_ticket - чтоб создать задачу
        /close_ticket {номер} - чтоб закрыть задачу
        /help - список команд
        """)
        return

    await message.answer("Добро пожаловать! Как тебя зовут? (ФИО)")
    await state.set_state(RegistrationStates.waiting_for_full_name)


@router.message(RegistrationStates.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext):
    text = await require_text(message)
    if text is None:
        return
    await state.update_data(full_name=text)
    await message.answer("Какая у тебя должность?")
    await state.set_state(RegistrationStates.waiting_for_job_title)


@router.message(RegistrationStates.waiting_for_job_title)
async def process_job_title(message: Message, state: FSMContext):
    text = await require_text(message)
    if text is None:
        return
    await state.update_data(job_title=text)
    await message.answer("Какой у тебя кабинет?")
    await state.set_state(RegistrationStates.waiting_for_cabinet)


@router.message(RegistrationStates.waiting_for_cabinet)
async def process_cabinet(message: Message, state: FSMContext, session):
    text = await require_text(message)
    if text is None:
        return
    data = await state.get_data()
    full_name = data["full_name"]
    job_title = data["job_title"]
    cabinet = text

    try:
        user_service.register_user(
            session,
            telegram_id=message.from_user.id,
            full_name=full_name,
            job_title=job_title,
            cabinet=cabinet,
            role=Role.user
        )
    except UserValidationError as e:
        await message.answer(f"Ошибка: {e}\n\nДавай начнём заново. Как тебя зовут? (ФИО)")
        await state.set_state(RegistrationStates.waiting_for_full_name)
        return

    await state.clear()
    await message.answer("Готово, ты зарегистрирован!")