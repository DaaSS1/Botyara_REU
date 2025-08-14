from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from bot.handlers import start, tasks, solution

storage = MemoryStorage()

async def main():
    bot = Bot(token = "")
    dp = Dispatcher(storage = storage)
    # подключение миддлваря
    # подключение роутера
    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(solution.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())