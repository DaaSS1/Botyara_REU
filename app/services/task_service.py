from aiogram.types import Message
from app.core.database import async_session_maker
from app.models.task import Tasks
from sqlalchemy import update, select
import logging

logger = logging.getLogger(__name__)

async def save_user_image(message: Message, task_id: int):
    """Сохраняет фото от пользователя в JSON-поле images у задачи."""

    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer("❌ Пришлите фото или файл (document).")
        return None
    try:
        async with async_session_maker() as session:
            # Сначала получаем уже сохраненные фото
            result = await session.execute(
                select(Tasks.images).where(Tasks.task_id == task_id)
            )
            current_images = result.scalar_one_or_none() or []

            # Добавляем новое фото
            updated_images = current_images + [file_id]

            # Обновляем запись
            stmt = (
                update(Tasks)
                .where(Tasks.task_id == task_id)
                .values(images=updated_images)
            )
            await session.execute(stmt)
            await session.commit()

        logger.info(f"✅ Сохранили фото для задачи {task_id}: {file_id}")
        return updated_images

    except Exception as e:
        logger.error(f"Ошибка сохранения фото: {e}")
        return None
