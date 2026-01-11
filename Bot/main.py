import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN
from app.database.core import create_table
from app.handlers import router as main_router

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
if not os.path.exists("logs"):
    os.makedirs("logs")

logger = logging.getLogger('bot_actions')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('logs/actions.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
# -----------------------------

async def main():
    # Проверка папок
    for folder in ["Assets", "payments"]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Инициализация БД
    await create_table()
    from app.database.requests import sync_courses_from_config
    await sync_courses_from_config()

    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем роутеры
    dp.include_router(main_router)

    logger.info("🤖 Бот запускается...")

    # Установка команд меню
    await bot.set_my_commands([
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/buy", description="Купить курс")
    ])

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🚫 Бот остановлен.")