from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.api_client import create_task_api, get_user_api
from bot.keyboards import set_subject, set_solve_method
import logging

router = Router()
logger = logging.getLogger(__name__)

# Новый порядок: метод → предмет → текст
class TaskStates(StatesGroup):
    waiting_for_method = State()
    waiting_for_subject = State()
    waiting_for_text = State()


# --- Старт создания задачи ---
@router.callback_query(F.data == "create_task")
async def start_task_creation(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(f"=== CREATE_TASK: User {user_id} начал создание задачи ===")
    await callback.message.answer("🤔 Как решить задачу?", reply_markup=await set_solve_method())
    await state.set_state(TaskStates.waiting_for_method)
    logger.info(f"Состояние пользователя {user_id} установлено: waiting_for_method")


# --- Метод решения ---
@router.callback_query(TaskStates.waiting_for_method)
async def handle_method(callback: CallbackQuery, state: FSMContext):
    solve_method = callback.data
    user_id = callback.from_user.id

    await state.update_data(solve_method=solve_method)
    logger.info(f"=== METHOD: User {user_id} выбрал способ: '{solve_method}' ===")

    await callback.message.answer("🧠 Выбери предмет задачи:", reply_markup=await set_subject())
    await state.set_state(TaskStates.waiting_for_subject)


# --- Предмет задачи ---
@router.callback_query(TaskStates.waiting_for_subject)
async def handle_subject(callback: CallbackQuery, state: FSMContext):
    subject = callback.data
    user_id = callback.from_user.id

    await state.update_data(subject=subject)
    logger.info(f"=== SUBJECT: User {user_id} выбрал предмет: '{subject}' ===")

    await callback.message.answer("✏️ Пришли текст задачи или прикрепи файл (PDF/фото)")
    await state.set_state(TaskStates.waiting_for_text)


# --- Текст / файл задачи ---
@router.message(TaskStates.waiting_for_text)
async def handle_task_text(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id

    logger.info(f"=== TASK_TEXT: User {user_id} прислал текст/файл ===")

    content = ""
    file_id = None
    if message.text:
        content = message.text
    elif message.document:
        content = f"[Файл] {message.document.file_name}"
    elif message.photo:
        file_id = message.photo[-1].file_id

    await state.update_data(problem_text=content, file_id=file_id)

    # достаем solve_method и subject
    solve_method = data["solve_method"]
    subject = data["subject"]

    # статус по solve_method
    status = "pending_ai" if solve_method == "ai_solve_usage" else "waiting_for_solver"

    try:
        # проверка что юзер есть в БД
        user = await get_user_api(user_id)
        logger.info(f"Пользователь найден в БД: {user}")

        task_data = {
            "user_id": user_id,
            "problem_text": content,
            "subject": subject,
            "status": status,
            "deadline": None,
            "solver_id": None,
            "file_id": file_id
        }

        result = await create_task_api(task_data)
        await message.answer("✅ Задача успешно создана!")
        logger.info(f"Задача создана на сервере: {result}")
    except Exception as e:
        await message.answer(f"Ошибка при создании задачи: {e}")
        logger.error(f"Ошибка create_task_api: {e}")

    await state.clear()
    logger.info(f"Состояние пользователя {user_id} очищено")
