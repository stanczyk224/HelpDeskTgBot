from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import Session

from Exceptions.AccessDeniedError import AccessDeniedError
from Exceptions.UserValidationError import UserValidationError
from Keyboards.list_users_keyboard import (
    users_list_keyboard,
    user_keyboard,
)
from Service import user_service
from Service.access_control import ensure_is_admin


router = Router()

USERS_PER_PAGE = 10


# ============================================================
# /all_users
# ============================================================

@router.message(Command("all_users"))
async def all_users_handler(
    message: Message,
    session: Session
):
    actor = user_service.get_user_by_telegram_id(
        session=session,
        telegram_id=message.from_user.id,
    )

    if actor is None:
        await message.answer("❌ Пользователь не найден.")
        return

    try:
        users, total_users = user_service.get_users_page(
            session=session,
            actor=actor,
            page=1,
            per_page=USERS_PER_PAGE,
        )
    except AccessDeniedError:
        await message.answer(
            "⛔ Только администратор может просматривать пользователей."
        )
        return

    total_pages = max(
        1,
        (total_users + USERS_PER_PAGE - 1) // USERS_PER_PAGE,
    )

    await message.answer(
        "👥 Список пользователей:",
        reply_markup=users_list_keyboard(
            users=users,
            page=1,
            total_pages=total_pages,
        ),
    )


# ============================================================
# ПАГИНАЦИЯ
# ============================================================

@router.callback_query(F.data.startswith("users:page:"))
async def users_page_handler(
    callback: CallbackQuery,
    session: Session,
):
    page = int(callback.data.split(":")[2])

    actor = user_service.get_user_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )

    if actor is None:
        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True,
        )
        return

    try:
        users, total_users = user_service.get_users_page(
            session=session,
            actor=actor,
            page=page,
            per_page=USERS_PER_PAGE,
        )
    except AccessDeniedError:
        await callback.answer(
            "⛔ Только администратор может просматривать пользователей.",
            show_alert=True,
        )
        return

    total_pages = max(
        1,
        (total_users + USERS_PER_PAGE - 1) // USERS_PER_PAGE,
    )

    # Защита от несуществующей страницы
    if page > total_pages:
        page = total_pages

        users, total_users = user_service.get_users_page(
            session=session,
            actor=actor,
            page=page,
            per_page=USERS_PER_PAGE,
        )

    await callback.message.edit_reply_markup(
        reply_markup=users_list_keyboard(
            users=users,
            page=page,
            total_pages=total_pages,
        )
    )

    await callback.answer()


# ============================================================
# КНОПКА НОМЕРА СТРАНИЦЫ
# ============================================================

@router.callback_query(F.data == "users:noop")
async def users_noop_handler(
    callback: CallbackQuery,
):
    await callback.answer()


# ============================================================
# ОТКРЫТЬ ПОЛЬЗОВАТЕЛЯ
# ============================================================

@router.callback_query(F.data.regexp(r"^user:\d+:\d+$"))
async def user_info_handler(
    callback: CallbackQuery,
    session: Session,
):
    parts = callback.data.split(":")

    user_id = int(parts[1])
    page = int(parts[2])

    actor = user_service.get_user_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )

    if actor is None:
        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True,
        )
        return

    try:
        ensure_is_admin(actor)

        user = user_service.get_user_by_id(
            session=session,
            user_id=user_id,
        )

        if user is None:
            await callback.answer(
                "❌ Пользователь не найден.",
                show_alert=True,
            )
            return

    except AccessDeniedError:
        await callback.answer(
            "⛔ Только администратор.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        f"👤 Пользователь\n\n"
        f"🆔 ID: {user.id}\n"
        f"👨‍💼 ФИО: {user.full_name}\n"
        f"💼 Должность: {user.job_title}\n"
        f"🚪 Кабинет: {user.cabinet}\n"
        f"🔐 Роль: {user.role}",
        reply_markup=user_keyboard(
            user=user,
            page=page,
        ),
    )

    await callback.answer()


# ============================================================
# ПОВЫСИТЬ ДО АДМИНИСТРАТОРА
# ============================================================

@router.callback_query(F.data.regexp(r"^user:promote:\d+:\d+$"))
async def promote_user_handler(
    callback: CallbackQuery,
    session: Session,
):
    parts = callback.data.split(":")

    user_id = int(parts[2])
    page = int(parts[3])

    actor = user_service.get_user_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )

    if actor is None:
        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True,
        )
        return

    try:
        user_service.promote_to_admin(
            session=session,
            actor=actor,
            user_id=user_id,
        )

    except AccessDeniedError:
        await callback.answer(
            "⛔ Только администратор.",
            show_alert=True,
        )
        return

    except UserValidationError as e:
        await callback.answer(
            f"❌ {e}",
            show_alert=True,
        )
        return

    user = user_service.get_user_by_id(
        session=session,
        user_id=user_id,
    )

    if user is None:
        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        f"👤 Пользователь\n\n"
        f"🆔 ID: {user.id}\n"
        f"👨‍💼 ФИО: {user.full_name}\n"
        f"💼 Должность: {user.job_title}\n"
        f"🚪 Кабинет: {user.cabinet}\n"
        f"🔐 Роль: {user.role}",
        reply_markup=user_keyboard(
            user=user,
            page=page,
        ),
    )

    await callback.answer(
        "✅ Пользователь повышен до администратора."
    )


# ============================================================
# ПОНИЗИТЬ ДО ОБЫЧНОГО ПОЛЬЗОВАТЕЛЯ
# ============================================================

@router.callback_query(F.data.regexp(r"^user:demote:\d+:\d+$"))
async def demote_user_handler(
    callback: CallbackQuery,
    session: Session,
):
    parts = callback.data.split(":")

    user_id = int(parts[2])
    page = int(parts[3])

    actor = user_service.get_user_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )

    if actor is None:
        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True,
        )
        return

    try:
        user_service.demote_to_user(
            session=session,
            actor=actor,
            user_id=user_id,
        )

    except AccessDeniedError:
        await callback.answer(
            "⛔ Только администратор.",
            show_alert=True,
        )
        return

    except UserValidationError as e:
        await callback.answer(
            f"❌ {e}",
            show_alert=True,
        )
        return

    user = user_service.get_user_by_id(
        session=session,
        user_id=user_id,
    )

    if user is None:
        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        f"👤 Пользователь\n\n"
        f"🆔 ID: {user.id}\n"
        f"👨‍💼 ФИО: {user.full_name}\n"
        f"💼 Должность: {user.job_title}\n"
        f"🚪 Кабинет: {user.cabinet}\n"
        f"🔐 Роль: {user.role}",
        reply_markup=user_keyboard(
            user=user,
            page=page,
        ),
    )

    await callback.answer(
        "✅ Пользователь понижен до обычного пользователя."
    )


# ============================================================
# УДАЛИТЬ ПОЛЬЗОВАТЕЛЯ
# ============================================================

@router.callback_query(F.data.regexp(r"^user:delete:\d+:\d+$"))
async def delete_user_handler(
    callback: CallbackQuery,
    session: Session,
):
    parts = callback.data.split(":")

    user_id = int(parts[2])
    page = int(parts[3])

    actor = user_service.get_user_by_telegram_id(
        session=session,
        telegram_id=callback.from_user.id,
    )

    if actor is None:
        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True,
        )
        return

    try:
        user_service.remove_user(
            session=session,
            actor=actor,
            user_id=user_id,
        )

    except AccessDeniedError:
        await callback.answer(
            "⛔ Только администратор.",
            show_alert=True,
        )
        return

    except UserValidationError as e:
        await callback.answer(
            f"❌ {e}",
            show_alert=True,
        )
        return

    users, total_users = user_service.get_users_page(
        session=session,
        actor=actor,
        page=page,
        per_page=USERS_PER_PAGE,
    )

    total_pages = max(
        1,
        (total_users + USERS_PER_PAGE - 1) // USERS_PER_PAGE,
    )

    # Если после удаления текущей страницы больше не существует
    if page > total_pages:
        page = total_pages

        users, total_users = user_service.get_users_page(
            session=session,
            actor=actor,
            page=page,
            per_page=USERS_PER_PAGE,
        )

    await callback.message.edit_text(
        "👥 Список пользователей:",
        reply_markup=users_list_keyboard(
            users=users,
            page=page,
            total_pages=total_pages,
        ),
    )

    await callback.answer(
        "🗑 Пользователь удалён."
    )

