from aiogram.types import Message

from Keyboards.main_menu_keyboards import cancel_ticket_creation_keyboard


async def require_text(message: Message) -> str | None:
    if message.text is None:
        await message.answer("Пожалуйста, отправь текстовое сообщение")
        return None
    return message.text

async def ask(
        message: Message,
        text: str
):
    await message.answer(
        text,
        reply_markup=cancel_ticket_creation_keyboard()
    )