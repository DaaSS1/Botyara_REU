from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
import asyncio
import redis.asyncio as redis
from bot.handlers import start, tasks, solution
from bot.middlewares import AlbumMiddleware
from config import BOT_TOKEN, REDIS_URL
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

# Создание Redis клиента
redis_client = redis.from_url(REDIS_URL)
storage = RedisStorage(redis_client)

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    # Подключение middleware
    dp.message.middleware(AlbumMiddleware())

    # Удаляем старые вебхуки
    await bot.delete_webhook(drop_pending_updates=True)

    # Подключаем роутеры
    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(solution.router)

    # Старт polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
