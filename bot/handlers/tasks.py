from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.services.task_service import save_user_image
from bot.api_client import create_task_api, get_user_api
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.crud import create_task
from bot.keyboards import set_subject, set_solve_method
from app.schemas.tasks import TaskCreate
from app.models.task import Tasks
import logging

router = Router()
logger = logging.getLogger(__name__)

# Этапы ввода задачи
class TaskStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_subject = State()
    waiting_for_method = State()

@router.callback_query(F.data == "create_task")
async def start_task_creation(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(f"=== CREATE_TASK: User {user_id} начал создание задачи ===")
    await callback.message.answer("✏️ Пришли текст задачи или прикрепи файл (PDF/фото)")
    await state.set_state(TaskStates.waiting_for_text)
    logger.info(f"Состояние пользователя {user_id} установлено: waiting_for_text")


@router.message(TaskStates.waiting_for_text)
async def handle_task_text(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"=== TASK_TEXT: User {user_id} прислал текст задачи ===")

    content = ""
    file_id = None
    if message.text:
        content = message.text
    elif message.document:
        content = f"[Файл] {message.document.file_name}"
    elif message.photo:
        content = "PHOTO"
        file_id = message.photo[-1].file_id

    await state.update_data(problem_text=content, file_id = file_id)
    logger.info(f"User {user_id} прислал текст задачи: {content}")
    await message.answer("🧠 Выбери предмет задачи:", reply_markup=await set_subject())
    await state.set_state(TaskStates.waiting_for_subject)
    logger.info(f"Состояние пользователя {user_id} изменено на: waiting_for_subject")


@router.callback_query(TaskStates.waiting_for_subject)
async def handle_subject(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    subject = callback.data
    logger.info(f"=== SUBJECT: User {user_id} выбрал предмет: '{subject}' ===")

    await state.update_data(subject=subject)
    await callback.message.answer("🤔 Как решить задачу?", reply_markup=await set_solve_method())
    await state.set_state(TaskStates.waiting_for_method)

    logger.info(f"Состояние пользователя {user_id} изменено на waiting_for_method")

# Обработчик для отладки кнопок выбора предмета (если основной не сработал)
@router.callback_query(F.data.in_(["math", "prog", "inf_sys"]))
async def debug_subject_buttons(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    logger.warning(f"DEBUG_SUBJECT: Кнопка '{callback.data}' нажата в состоянии '{current_state}' от пользователя {callback.from_user.id}")
    await callback.answer(f"Отладка: кнопка {callback.data} в состоянии {current_state}")


@router.callback_query(TaskStates.waiting_for_method)
async def handle_method(callback: CallbackQuery, state: FSMContext):
    solve_method = callback.data
    data = await state.get_data()
    user_id = callback.from_user.id

    logger.info(f"=== METHOD: Получен callback для метода решения: '{solve_method}' от пользователя {user_id} ===")
    logger.info(f"Данные из состояния: {data}")

    # Можно добавить статус в зависимости от метода
    status = "pending_ai" if solve_method == "ai_solve_usage" else "waiting_for_solver"
    logger.info(f"Установлен статус задачи: {status}")

    try:
        # Проверяем, что пользователь существует в БД
        user = await get_user_api(user_id)
        logger.info(f"Пользователь найден в БД: {user}")

        task_data = {
            "user_id": user_id,  # Используем tg_user_id напрямую
            "problem_text": data["problem_text"],
            "subject": data["subject"],
            "status": status,  # Используем правильный статус
            "deadline": None,
            "solver_id": None,# Добавляем solver_id
            "file_id": data.get("file_id")
        }
        logger.info(f"Отправка задачи от пользователя {user_id} на сервер: {task_data}")

        result = await create_task_api(task_data)
        await callback.message.answer(f"✅ Задача успешно создана!")
        logger.info(f"Задача создана на сервере: {result}")
    except Exception as e:
        await callback.message.answer(f"ХАХАХАХАХ ЛОШАРА ОШИБКА {e}")
        logger.error(f"Ошибка при вызове create_task_api для пользователя {user_id}: {e}")
    await state.clear()
    logger.info(f"Состояние пользователя {user_id} очищено")