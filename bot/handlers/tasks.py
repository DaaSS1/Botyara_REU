from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from bot.api_client import create_task_api, get_user_api
from bot.keyboards import set_subject, set_solve_method, big_text_with_back, prices_back_keyboard, get_main_menu, prices
import logging

router = Router()
logger = logging.getLogger(__name__)


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
    logger.info(f"=== METHOD: User {user_id} выбрал '{solve_method}' ===")

    await callback.message.edit_text("🧠 Выбери предмет задачи:", reply_markup=await set_subject())
    await state.set_state(TaskStates.waiting_for_subject)

# --- Предмет ---
@router.callback_query(TaskStates.waiting_for_subject)
async def handle_subject(callback: CallbackQuery, state: FSMContext):
    subject = callback.data
    user_id = callback.from_user.id

    await state.update_data(subject=subject)
    logger.info(f"=== SUBJECT: User {user_id} выбрал '{subject}' ===")

    long_text = (
        "Пожалуйста, укажите следующие данные:\n"
        "— Тип работы (контрольная, зачет, экзамен и т.д.)\n"
        "— Укажите дату и время пары (если нужно).\n"
        "— Обязательно укажите дедлайн.\n"
        "— Опишите тип задания.\n"
        "— Можно добавить преподавателя.\n\n"
        "💰 Оплата по полной предоплате.\n"
        "⏰ Если оплата не внесена в течение 2 часов после уведомления — задача не принимается."
    )
    # Кнопки: Прайс (покажем отдельным сообщением) и Назад (вернуть к выбору предмета)
    await callback.message.edit_text(long_text, reply_markup=await big_text_with_back(back_cb="back_to_subject"))
    await state.set_state(TaskStates.waiting_for_text)

# --- Назад к выбору предмета (callback) ---
@router.callback_query(F.data == "back_to_subject")
async def back_to_subject(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🧠 Выбери предмет задачи:", reply_markup=await set_subject())
    await state.set_state(TaskStates.waiting_for_subject)

# --- Показать прайс (из главного меню) ---
@router.callback_query(F.data == "show_prices")
async def show_prices(callback: CallbackQuery):
    """
    Универсальный handler для кнопки 'Прайс' из main menu или из FSM.
    Поведение:
      - если исходное сообщение было главное меню — редактируем сообщение (чтобы можно было вернуться назад)
      - если исходное сообщение находится в процессе FSM (в рамках create task) —
        мы отправляем отдельное сообщение с прайсом и кнопкой 'Назад', которая удалит прайс-сообщение.
    """
    # если сообщение содержит клавиатуру main_menu (попробуем понять по тексту)
    text = (callback.message.text or "").lower()
    # очень простая эвристика: если в сообщении есть слово "привет" или "главное меню" — считаем это меню
    if "привет" in text or "создать заявку" in text or "полезные" in text:
        # редактируем исходное сообщение — добавляем кнопку "Назад" которая вернёт главное меню
        await callback.message.edit_text(prices, reply_markup=await prices_back_keyboard(back_cb="back_to_main"))
    else:
        # отправляем отдельное сообщение с прайсом, чтобы не ломать FSM-экран
        await callback.message.answer(prices, reply_markup=await prices_back_keyboard(back_cb="back_to_task"))

# --- Назад в главное меню (редактируем сообщение обратно) ---
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("Выберите действие:", reply_markup=await get_main_menu())

# --- Назад к заполнению задачи (удаляем прайс-сообщение) ---
@router.callback_query(F.data == "back_to_task")
async def back_to_task(callback: CallbackQuery):
    # удаляем сообщение с прайсом — пользователь увидит исходный экран заполнения заявки
    try:
        await callback.message.delete()
    except Exception:
        # если удалить нельзя — просто скрываем alert
        pass
    await callback.answer("Возвращаемся к заполнению заявки.", show_alert=False)

# --- Текст задачи ---
@router.message(TaskStates.waiting_for_text)
async def handle_task_text(message: Message, state: FSMContext):
    user_id = message.from_user.id
    problem_text = message.text

    await state.update_data(problem_text=problem_text, file_ids=[])
    logger.info(f"=== TEXT: User {user_id} прислал текст ===")

    await message.answer("📎 Теперь прикрепи фото или файлы. Когда закончишь — напиши 'готово'.")
    await state.set_state(TaskStates.waiting_for_files)


# --- Файлы задачи ---
@router.message(TaskStates.waiting_for_files)
async def handle_task_files(
    message: Message,
    state: FSMContext,
    album: list[Message] | None = None,
):
    data = await state.get_data()
    user_id = message.from_user.id
    file_ids: list[str] = data.get("file_ids", [])

    # --- Если закончил ---
    if message.text and message.text.lower() == "готово":
        problem_text = data.get("problem_text")
        solve_method = data.get("solve_method")
        subject = data.get("subject")
        file_ids = data.get("file_ids", [])

        status = "pending_ai" if solve_method == "ai_solve_usage" else "waiting_for_solver"

        try:
            user = await get_user_api(user_id)
            logger.info(f"Пользователь найден в БД (get_user_api): {user!r}")

            # используем Telegram ID напрямую, т.к. ForeignKey -> tg_user_id
            task_data = {
                "user_id": user_id,  # это tg_user_id
                "problem_text": problem_text,
                "subject": subject,
                "status": status,
                "deadline": None,
                "solver_id": None,
                "images": [f["file_id"] if isinstance(f, dict) else f for f in file_ids],
            }

            logger.info("=== Payload create_task_api ===")
            logger.info(task_data)

            result = await create_task_api(task_data)
            await message.answer("✅ Задача успешно создана!")

            # уведомляем админов
            if not ADMIN_IDS:
                logger.warning("ADMIN_IDS пуст — уведомления не отправлены.")
            else:
                for raw in ADMIN_IDS:
                    try:
                        chat_id = int(raw)
                        await message.bot.send_message(
                            chat_id=chat_id,
                            text="📋 Новая задача создана. Ознакомьтесь с условиями и возьмите в работу.",
                        )
                        logger.info(f"Уведомление отправлено администратору {chat_id}")
                    except Exception as e:
                        logger.exception(f"Ошибка уведомления админа {raw}: {e}")

            logger.info(f"Задача создана: {result}")
        except Exception as e:
            await message.answer("❌ Ошибка при создании задачи. Попробуйте позже.")
            logger.exception(f"Ошибка create_task_api: {e}")

        await state.clear()
        logger.info(f"Состояние пользователя {user_id} очищено.")
        return

    # --- Добавление файлов ---
    new_files = []
    if album:
        for msg in album:
            if msg.photo:
                new_files.append({"file_id": msg.photo[-1].file_id, "type": "photo"})
            elif msg.document:
                new_files.append({"file_id": msg.document.file_id, "type": "document"})
        await message.answer(f"✅ Добавлено {len(new_files)} файлов. Пришли ещё или напиши 'готово'.")
    elif message.photo:
        new_files.append({"file_id": message.photo[-1].file_id, "type": "photo"})
        await message.answer("✅ Фото добавлено. Пришли ещё или напиши 'готово'.")
    elif message.document:
        new_files.append({"file_id": message.document.file_id, "type": "document"})
        await message.answer("✅ Файл добавлен. Пришли ещё или напиши 'готово'.")

    file_ids.extend(new_files)
    await state.update_data(file_ids=file_ids)
    logger.info(f"=== FILE(S): User {user_id} добавил {len(new_files)} файлов, всего: {len(file_ids)} ===")
