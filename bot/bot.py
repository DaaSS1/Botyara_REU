from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from bot.handlers import start, tasks, solution
from bot.middlewares import AlbumMiddleware
storage = MemoryStorage()

async def main():
    bot = Bot(token = "8366768334:AAFrRoi2g19PawY3dWl15ZFInGxCrLp_pjk")
    dp = Dispatcher(storage = storage)

    dp.message.middleware(AlbumMiddleware())

    # подключение роутера
    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(solution.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())