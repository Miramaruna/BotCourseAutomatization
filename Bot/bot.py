# region imports

import asyncio
import logging

from config import TOKEN
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from config import *

from app.handlers import r

# endregion

if not TOKEN:
    raise ValueError("🚨 TOKEN environment variable is not set")

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
# Создаем логгер
logger = logging.getLogger('bot_actions')
logger.setLevel(logging.INFO)

# Формат записи: Время - Уровень - Сообщение
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Пишем в файл
file_handler = logging.FileHandler('actions.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Пишем в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
# -----------------------------

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    # Используем наш настроенный логгер
    logger.info("🤖 Бот запускается...")
    
    dp.include_router(r)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True, polling_timeout=30)
    
    await bot.set_my_commands([
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/buy", description="Купить курс")
    ])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🚫 Бот остановлен.")