from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.filters import Command
import logging

from app.core.crud import get_task
from bot.api_client import get_user_api, get_available_tasks_api, assign_task_to_solver_api, create_solution_api, \
    get_task_api
from bot.keyboards import create_task_list_keyboard, create_task_choice_keyboard
import re
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State,StatesGroup

router = Router()
logger = logging.getLogger(__name__)

class SendSolutionStates(StatesGroup):
    waiting_for_photo = State()

@router.message(Command(commands=["check_tasks"]))
async def check_tasks(message: Message):
    """Команда для исполнителей - показать доступные задачи"""
    user_id = message.from_user.id

    try:
        # Проверяем, что пользователь существует и является исполнителем
        user = await get_user_api(user_id)
        if not user:
            await message.answer("❌ Вы не зарегистрированы в системе")
            return

        # TODO: Добавить проверку роли исполнителя
        # if user.get("role") != "solver":
        #     await message.answer("❌ Эта команда доступна только исполнителям")
        #     return

        await message.answer("🔍 Ищу доступные задачи...")

        # Получаем доступные задачи
        available_tasks = await get_available_tasks_api()

        if not available_tasks:
            await message.answer("📭 Нет доступных задач на данный момент")
            return

        # Показываем список задач
        await message.answer(
            f"📋 Найдено {len(available_tasks)} доступных задач:",
            reply_markup=await create_task_list_keyboard(available_tasks)
        )

    except Exception as e:
        logger.error(f"Ошибка при получении задач для пользователя {user_id}: {e}")
        await message.answer("❌ Ошибка при получении задач. Попробуйте позже.")

@router.callback_query(F.data == "new_tasks")
async def show_available_tasks(callback: CallbackQuery):
    """Показать доступные задачи (альтернативный способ)"""
    user_id = callback.from_user.id

    try:
        available_tasks = await get_available_tasks_api()

        if not available_tasks:
            await callback.message.edit_text("📭 Нет доступных задач на данный момент")
            return

        await callback.message.edit_text(
            f"📋 Найдено {len(available_tasks)} доступных задач:",
            reply_markup=await create_task_list_keyboard(available_tasks)
        )

    except Exception as e:
        logger.error(f"Ошибка при получении задач для пользователя {user_id}: {e}")
        await callback.message.edit_text("❌ Ошибка при получении задач")

@router.callback_query(F.data == "refresh_tasks")
async def refresh_tasks_list(callback: CallbackQuery):
    """Обновить список доступных задач"""
    user_id = callback.from_user.id

    try:
        available_tasks = await get_available_tasks_api()

        if not available_tasks:
            await callback.message.edit_text("📭 Нет доступных задач на данный момент")
            return

        await callback.message.edit_text(
            f"📋 Найдено {len(available_tasks)} доступных задач:",
            reply_markup=await create_task_list_keyboard(available_tasks)
        )

    except Exception as e:
        logger.error(f"Ошибка при обновлении задач для пользователя {user_id}: {e}")
        await callback.answer("❌ Ошибка при обновлении списка")

@router.callback_query(F.data.startswith("view_task_"))
async def view_task_details(callback: CallbackQuery):
    """Показать детали конкретной задачи"""
    user_id = callback.from_user.id
    task_id = int(callback.data.split("_")[2])

    try:
        # Получаем детали задачи
        available_tasks = await get_available_tasks_api()
        task = next((t for t in available_tasks if t["task_id"] == task_id), None)

        if not task:
            await callback.answer("❌ Задача не найдена или уже назначена")
            return

        task_text = f"""
📝 **Детали задачи #{task_id}**

📚 **Предмет:** {task['subject']}
📄 **Текст задачи:** {task['problem_text']}
⏰ **Дедлайн:** {task['deadline'] or 'Не указан'}
📊 **Статус:** {task['status']}

Хотите взять эту задачу?
        """.strip()

        kb = await create_task_choice_keyboard(task_id)

        images = task.get("images") or []
        if images:
            # если фото есть → шлём альбом
            media = []
            for i, f_id in enumerate(images):
                if i == 0:
                    media.append(InputMediaPhoto(media=f_id, caption=task_text))
                else:
                    media.append(InputMediaPhoto(media=f_id))

            await callback.message.answer_media_group(media=media)
            # отдельно кидаем клавиатуру
            await callback.message.answer("👇 Действия по задаче:", reply_markup=kb)
        else:
            await callback.message.answer(task_text, reply_markup=kb)

    except Exception as e:
        logger.error(f"Ошибка при просмотре задачи {task_id} пользователем {user_id}: {e}")
        await callback.answer("❌ Ошибка при загрузке задачи")

@router.callback_query(F.data.startswith("accept_task_"))
async def accept_task(callback: CallbackQuery, state: FSMContext):
    """Исполнитель принимает задачу"""
    user_id = callback.from_user.id
    task_id = int(callback.data.split("_")[2])

    try:
        # Назначаем задачу исполнителю
        result = await assign_task_to_solver_api(task_id, user_id)
        new_text = (
            f"✅ **Задача #{task_id} успешно назначена вам!**\n\n"
            f"📝 Текст: {result['problem_text'][:100]}...\n"
            f"📚 Предмет: {result['subject']}\n\n"
            f"Приступайте к решению! 🚀"
        )

        if callback.message.photo:
            await callback.message.edit_caption(new_text)
        else:
            await callback.message.edit_text(new_text)

        logger.info(f"Пользователь {user_id} принял задачу {task_id}")

        task = await get_task_api(task_id)
        task_user_id = task.get("user_id")
        await callback.bot.send_message(chat_id=task_user_id, text="📢 Ваша задача принята исполнителем! В скором времени он пришлет решение. "
                 "Пожалуйста, произведите оплату 💳")


    except Exception as e:
        logger.error(f"Ошибка при назначении задачи {task_id} пользователю {user_id}: {e}")
        await callback.answer("❌ Ошибка при назначении задачи")

@router.callback_query(F.data.startswith("reject_task_"))
async def reject_task(callback: CallbackQuery):
    """Исполнитель отклоняет задачу"""
    user_id = callback.from_user.id
    task_id = int(callback.data.split("_")[2])

    try:
        # Возвращаемся к списку задач
        available_tasks = await get_available_tasks_api()

        if not available_tasks:
            await callback.message.edit_text("📭 Нет других доступных задач")
            return

        await callback.message.edit_text(
            f"📋 Доступные задачи (задача #{task_id} отклонена):",
            reply_markup=await create_task_list_keyboard(available_tasks)
        )

        logger.info(f"Пользователь {user_id} отклонил задачу {task_id}")

    except Exception as e:
        logger.error(f"Ошибка при отклонении задачи {task_id} пользователем {user_id}: {e}")
        await callback.answer("❌ Ошибка при отклонении задачи")

@router.message(F.text.regexp(r"^/send_solution_(\d+)$"))
async def start_solution(message: Message,state: FSMContext):
    m = re.match(r"^/send_solution_(\d+)$", message.text)
    task_id = int(m.group(1))
    await state.update_data(current_task_id = task_id)
    await state.set_state(SendSolutionStates.waiting_for_photo)
    await message.answer(f"Окей, жду фото решения для задачи #{task_id}")

@router.message(SendSolutionStates.waiting_for_photo, F.photo)
async def send_photo_solution(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data.get("current_task_id")
    if not task_id:
        await message.reply("Сначала укажи задачу командой: /send_solution_<task_id>")
        return

    solver_id = message.from_user.id
    file_ids = [p.file_id for p in message.photo]
    caption = message.caption or ""

    solution_data = {
        "solver_id": solver_id,
        "file_ids": file_ids,
        "caption": caption
    }

    try:
        resp = await create_solution_api(task_id, solution_data)
    except Exception:
        logger.exception("Create solution failed")
        await message.reply("Ошибка при сохранении решения. Пробуй позже сука")
        return

    task_user_id = resp.get("task_user_id")
    if not task_user_id:
        try:
            task = await get_task_api(task_id)
            task_user_id = task.get("user_id")
        except Exception:
            logger.exception("get_task_api failed")
            await message.reply("Решение сохранено, но не удалось уведомить заказчика.")
            return

    try:
        if len(file_ids) > 1:
            # несколько фото → альбом
            media = []
            for i, f_id in enumerate(file_ids):
                if i == 0:
                    media.append(InputMediaPhoto(media=f_id, caption="📤 Новое решение по Вашей задаче"))
                else:
                    media.append(InputMediaPhoto(media=f_id))
            await message.bot.send_media_group(chat_id=task_user_id, media=media)
        else:
            # одно фото
            await message.bot.send_photo(
                chat_id=task_user_id,
                photo=file_ids[0],
                caption="📤 Новое решение по Вашей задаче"
            )
    except Exception:
        logger.exception("send_photo to owner failed")
        await message.reply("Решение сохранено, но фото не доставлено заказчику.")
        return

    await message.reply(f"✅ Решение по задаче #{task_id} отправлено заказчику.")
    await state.clear()