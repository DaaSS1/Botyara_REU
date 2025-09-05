from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from httpx import HTTPStatusError

from bot.keyboards import get_main_menu
from bot.api_client import create_user_api, get_user_api, update_user_api
import logging
# импорт клавиатуры из keyboards.py

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command('start'))
async def start_command(message: Message):

    user_id = message.from_user.id
    tg_name = message.from_user.username or "unknown"
    logger.info(f"Обработка /start от {user_id}, username={tg_name}")

    try:
        user = await get_user_api(user_id)
        if tg_name!="unknown" and user.get("tg_name")!= tg_name:
            try:
                user = await update_user_api(user_id, {"tg_name": tg_name})
                logger.info(f"Обновил tg_name для {user_id} -> {tg_name}")
            except Exception as e:
                logger.warning(f"Не удалось обновить tg_name для {user_id}: {e}")
        if get_user_api(user_id):
            await message.answer(f"🔁 Привет снова, {user.get('tg_name') or tg_name}!")
            logger.info(f"Пользователь найден: {user}")

    except HTTPStatusError as e:
        if e.response.status_code == 400:
            user_data = {
                "tg_user_id": user_id,
                "tg_name": tg_name,
                "role": "student", #по айди из бд вставлять роль, пример - проект Тимохи
                "high_school": "РЭУ", # из инлайн кнопки
                "year": 1
            }
            try:
                created = await create_user_api(user_data)
                await message.answer(f"👋 Привет, {created['tg_name']}! Ты зарегистрирован.")
                logger.info(f"Новый пользователь зарегистрирован: {created}")
            except Exception as ce:
                await message.answer("Ошибка регистрации. Попробуйте позже.")
                logger.error(f"Ошибка при создании пользователя {user_id}: {ce}")
                return

        else:
            await message.answer("Сервис временно недоступен. Попробуйте позже.")
            logger.error(f"Ошибка при получении пользователя {user_id}: {e}")
            return

    except Exception as e:
        await message.answer("Сервис временно недоступен. Попробуйте позже.")
        logger.error(f"Неожиданная ошибка при /start для {user_id}: {e}")
        return

    await message.answer("Салам пополам, тапок",
                         reply_markup=await get_main_menu())