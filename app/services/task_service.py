from aiogram.types import Message
from datetime import datetime
from pathlib import Path

async def save_user_image(message: Message):
    user_id = message.from_user.id

    # 1. Получаем файл
    if not message.photo:
        return await message.answer("Пришли фото.")
    file = message.photo[-1]  # самое большое изображение
    #tg_file = await message.bot.get_file(file.file_id)
    file_id = file.file_id
    # # 2. Создаём папку пользователя
    # user_dir = Path(f"uploads/{user_id}")
    # user_dir.mkdir(parents=True, exist_ok=True)
    #
    # # 3. Формируем имя файла
    # timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # file_name = f"{timestamp}.jpg"
    # file_path = user_dir / file_name
    #
    # # 4. Сохраняем файл
    # await message.bot.download_file(tg_file.file_path, destination=file_path)

    return file_id