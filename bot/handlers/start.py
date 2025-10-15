from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_IDS
from bot.keyboards import get_main_menu, prices, show_tasks
from bot.api_client import create_user_api, get_user_api, update_user_api
import logging
# импорт клавиатуры из keyboards.py

router = Router()
logger = logging.getLogger(__name__)

async def send_menu_by_role(message: Message, role: str, tg_name: str):
    if role == "admin":
        await message.answer(f"👋 Привет, {tg_name}! Вы — админ.")
        await message.answer("Проверяй новые заявки", reply_markup=await show_tasks())
    else:
        await message.answer(f"👋 Привет, {tg_name}!", reply_markup=await get_main_menu())

@router.message(Command('start'))
async def start_command(message: Message):
    user_id = message.from_user.id
    tg_name = message.from_user.username or "unknown"
    logger.info(f"Обработка /start от {user_id}, username={tg_name}")

    try:
        user = await get_user_api(user_id)
    except Exception as e:
        user = None
        logger.warning(f"get_user_api failed for {user_id}: {e}")

    if user:
        # обновляем имя, если нужно
        try:
            if tg_name != 'unknown' and user.get("tg_name") != tg_name:
                await update_user_api(user_id, {"tg_name": tg_name})
        except Exception as e:
            logger.warning(f"Не удалось обновить tg_name для {user_id}: {e}")

        role = user.get("role") or ("admin" if user_id in ADMIN_IDS else "student")
        await send_menu_by_role(message, role, user.get("tg_name") or tg_name)
        return

    # создаём нового пользователя
    role = 'admin' if user_id in ADMIN_IDS else 'student'
    user_data = {
        "tg_user_id": user_id,
        "tg_name": tg_name,
        "role": role,
        "high_school": "РЭУ",
        "year": 1
    }
    try:
        created = await create_user_api(user_data)
        logger.info(f"Новый пользователь зарегистрирован: {created}")
        await send_menu_by_role(message, role, created.get("tg_name") or tg_name)
    except Exception as ce:
        logger.error(f"Ошибка при создании пользователя {user_id}: {ce}")
        await message.answer("Ошибка регистрации. Попробуйте позже.")