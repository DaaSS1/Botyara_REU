from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.filters import Command
import logging
from bot.api_client import get_user_api, get_available_tasks_api, assign_task_to_solver_api
from bot.keyboards import show_tasks, create_task_list_keyboard, create_task_choice_keyboard
from pathlib import Path

router = Router()
logger = logging.getLogger(__name__)

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

        # if task.get("file_id"):
        #     try:
        #         with open(task["file_id"]) :
        #             if task["file_id"].startswith("AgAC"):
        #                 await callback.message.answer_photo(task["file_id"], caption="Прикрепленный файл")
        #             else:
        #                 await callback.message.answer_document(task["file_id"], caption="Прикрепленный файл")
        #     except FileNotFoundError:
        #         await callback.answer("Файл не найден на сервере")

        # Формируем сообщение с деталями задачи
        task_text = f"""
📝 **Детали задачи #{task_id}**

📚 **Предмет:** {task['subject']}
📄 **Текст задачи:** {task['problem_text']}
⏰ **Дедлайн:** {task['deadline'] or 'Не указан'}
📊 **Статус:** {task['status']}

Хотите взять эту задачу?
        """.strip()

        kb = await create_task_choice_keyboard(task_id)

        if task.get("file_id"):
            await callback.message.answer_photo(
                photo=task["file_id"],
                caption=task_text,
                reply_markup=kb
            )
        else:
            await callback.message.answer(task_text, reply_markup=kb)
    except Exception as e:
        logger.error(f"Ошибка при просмотре задачи {task_id} пользователем {user_id}: {e}")
        await callback.answer("❌ Ошибка при загрузке задачи")

@router.callback_query(F.data.startswith("accept_task_"))
async def accept_task(callback: CallbackQuery):
    """Исполнитель принимает задачу"""
    user_id = callback.from_user.id
    task_id = int(callback.data.split("_")[2])

    try:
        # Назначаем задачу исполнителю
        result = await assign_task_to_solver_api(task_id, user_id)

        await callback.message.edit_text(
            f"✅ **Задача #{task_id} успешно назначена вам!**\n\n"
            f"📝 Текст: {result['problem_text'][:100]}...\n"
            f"📚 Предмет: {result['subject']}\n\n"
            f"Приступайте к решению! 🚀"
        )

        logger.info(f"Пользователь {user_id} принял задачу {task_id}")

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
