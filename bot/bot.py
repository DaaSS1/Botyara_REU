from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from bot.handlers import start, tasks, solution
from bot.middlewares import AlbumMiddleware
from app.core.config import BOT_TOKEN
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

storage = MemoryStorage()

async def main():
    bot = Bot(token = BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage = storage)

    dp.message.middleware(AlbumMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)

    # подключение роутера
    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(solution.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())