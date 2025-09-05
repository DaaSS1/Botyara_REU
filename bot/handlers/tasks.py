from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.core.config import ADMIN_IDS
from bot.api_client import create_task_api, get_user_api
from bot.keyboards import set_subject, set_solve_method
import logging

router = Router()
logger = logging.getLogger(__name__)


# Новый порядок: метод → предмет → текст → файлы
class TaskStates(StatesGroup):
    waiting_for_method = State()
    waiting_for_subject = State()
    waiting_for_text = State()
    waiting_for_files = State()


# --- Старт создания задачи ---
@router.callback_query(F.data == "create_task")
async def start_task_creation(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(f"=== CREATE_TASK: User {user_id} начал создание задачи ===")
    await callback.message.edit_text("🤔 Как решить задачу?", reply_markup=await set_solve_method())
    await state.set_state(TaskStates.waiting_for_method)


# --- Метод решения ---
@router.callback_query(TaskStates.waiting_for_method)
async def handle_method(callback: CallbackQuery, state: FSMContext):
    solve_method = callback.data
    user_id = callback.from_user.id

    await state.update_data(solve_method=solve_method)
    logger.info(f"=== METHOD: User {user_id} выбрал: '{solve_method}' ===")

    await callback.message.edit_text("🧠 Выбери предмет задачи:", reply_markup=await set_subject())
    await state.set_state(TaskStates.waiting_for_subject)


# --- Предмет задачи ---
@router.callback_query(TaskStates.waiting_for_subject)
async def handle_subject(callback: CallbackQuery, state: FSMContext):
    subject = callback.data
    user_id = callback.from_user.id

    await state.update_data(subject=subject)
    logger.info(f"=== SUBJECT: User {user_id} выбрал: '{subject}' ===")

    await callback.message.edit_text("✏️ Пришли текст задачи")
    await state.set_state(TaskStates.waiting_for_text)


# --- Текст задачи ---
@router.message(TaskStates.waiting_for_text)
async def handle_task_text(message: Message, state: FSMContext):
    user_id = message.from_user.id
    problem_text = message.text

    await state.update_data(problem_text=problem_text, file_ids=[])  # создаём список файлов
    logger.info(f"=== TEXT: User {user_id} прислал текст задачи ===")

    await message.answer("📎 Теперь прикрепи фото или файлы. Когда закончишь — напиши 'готово'")
    await state.set_state(TaskStates.waiting_for_files)


# --- Фото/файлы задачи (мультизагрузка + альбомы) ---
@router.message(TaskStates.waiting_for_files)
async def handle_task_files(
    message: Message,
    state: FSMContext,
    album: list[Message] | None = None,  # ← сюда AlbumMiddleware передаст альбом, если он есть
):
    data = await state.get_data()
    user_id = message.from_user.id
    file_ids: list[str] = data.get("file_ids", [])

    # --- Если юзер закончил ---
    if message.text and message.text.lower() == "готово":
        problem_text = data["problem_text"]
        solve_method = data["solve_method"]
        subject = data["subject"]
        file_ids = data.get("file_ids", [])

        status = "pending_ai" if solve_method == "ai_solve_usage" else "waiting_for_solver"

        try:
            user = await get_user_api(user_id)
            logger.info(f"Пользователь найден в БД: {user}")

            task_data = {
                "user_id": user_id,
                "problem_text": problem_text,
                "subject": subject,
                "status": status,
                "deadline": None,
                "solver_id": None,
                "images": [f["file_id"] if isinstance(f, dict) else f for f in file_ids]
            }

            result = await create_task_api(task_data)
            await message.answer("✅ Задача успешно создана!")

            logger.info(f"ADMIN_IDS: {ADMIN_IDS!r} (type={type(ADMIN_IDS)})")

            if not ADMIN_IDS:
                logger.warning("ADMIN_IDS пустой — никто не будет оповещён.")
            else:
                for raw in ADMIN_IDS:
                    try:
                        chat_id = int(raw)
                    except Exception:
                        logger.exception(f"Невалидный admin id: {raw!r}; пропускаем")
                        continue

                    try:
                        await message.bot.send_message(
                            chat_id=chat_id,
                            text="📋 Новая задача создана. Ознакомьтесь с условиями и возьмите в работу.",
                        )
                        logger.info(f"Уведомление отправлено администратору {chat_id}")
                    except Exception as e:
                        logger.exception(f"Не удалось отправить уведомление администратору {chat_id}: {e}")

            logger.info(f"Задача создана на сервере: {result}")
        except Exception as e:
            await message.answer(f"Ошибка при создании задачи: {e}")
            logger.error(f"Ошибка create_task_api: {e}")

        await state.clear()
        logger.info(f"Состояние пользователя {user_id} очищено")
        return

    # --- Добавление файлов ---
    new_files = []
    if album:
        for msg in album:
            if msg.photo:
                new_files.append({"file_id": msg.photo[-1].file_id, "type": "photo"})
            elif msg.document:
                new_files.append({"file_id": msg.document.file_id, "type": "document"})
        await message.answer(f"✅ Добавлено {len(new_files)} файлов. Пришли ещё или напиши 'готово'")
    elif message.photo:
        new_files.append({"file_id": message.photo[-1].file_id, "type": "photo"})
        await message.answer("✅ Фото добавлено. Пришли ещё или напиши 'готово'")
    elif message.document:
        new_files.append({"file_id": message.document.file_id, "type": "document"})
        await message.answer("✅ Файл добавлен. Пришли ещё или напиши 'готово'")

    # дополняем существующий список
    file_ids.extend(new_files)
    await state.update_data(file_ids=file_ids)

    logger.info(f"=== FILE(S): User {user_id} добавил {len(new_files)} файлов, всего: {len(file_ids)} ===")
