from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton


async def get_main_menu()-> InlineKeyboardMarkup:
    create_task = InlineKeyboardButton(text="📋 Создать заявку", callback_data="create_task")
    about_us = InlineKeyboardButton(text="ℹ️ О нас", callback_data="about_us")
    links = InlineKeyboardButton(text="Полезные ссылки", callback_data="links")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[create_task], [about_us], [links]])
    return keyboard

# При нажатии "Положить задачу в тапки":
#
# Бот запрашивает
# "Отправьте текст задачи или прикрепите файл (PDF/фото)"
#
# Кнопки быстрого выбора предмета:

async def set_subject() -> InlineKeyboardMarkup:
    math_button = InlineKeyboardButton(text="Высшая математика", callback_data='math')
    prog_button = InlineKeyboardButton(text="Программирование", callback_data="prog")
    inf_sys_button = InlineKeyboardButton(text="ИСиТ", callback_data="inf_sys")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[math_button], [prog_button], [inf_sys_button]])
    return keyboard

async def set_solve_method() -> InlineKeyboardMarkup:
    solver_solve = InlineKeyboardButton(text = "Отдать на решение исполнителю", callback_data="human_solve")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[solver_solve]])
    return keyboard

async def show_tasks() -> InlineKeyboardMarkup:
    show_button = InlineKeyboardButton(text = "Показать новые задачи", callback_data="new_tasks")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[show_button]])
    return keyboard

async def create_task_choice_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для выбора задачи исполнителем"""
    accept_button = InlineKeyboardButton(text="✅ Взять задачу", callback_data=f"accept_task_{task_id}")
    reject_button = InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_task_{task_id}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[accept_button, reject_button]])
    return keyboard

async def create_task_list_keyboard(tasks: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком доступных задач"""
    buttons = []
    for task in tasks:
        task_text = f"📝 {task['subject']} - {task['problem_text'][:30]}..."
        task_button = InlineKeyboardButton(text=task_text, callback_data=f"view_task_{task['task_id']}")
        buttons.append([task_button])

    refresh_button = InlineKeyboardButton(text="🔄 Обновить список", callback_data="refresh_tasks")
    buttons.append([refresh_button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def set_payment_method():
    pass

async def payment_by_link(): #юрл-кнопка оплатить
    pass
