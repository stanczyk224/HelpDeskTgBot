from aiogram.types import Message


async def require_text(message: Message) -> str | None:
    if message.text is None:
        await message.answer("Пожалуйста, отправь текстовое сообщение")
        return None
    return message.text