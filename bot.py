import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
import os
import json

# Загружаем переменные окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Не указан BOT_TOKEN в переменных окружения!")

google_credentials = json.loads(os.getenv("GOOGLE_CREDENTIALS", "{}"))

bot = Bot(token=TOKEN)
dp = Dispatcher()  # В aiogram 3.x Dispatcher создается без аргументов

@dp.message(Command("start"))  # Новый способ регистрации команды
async def start(message: Message):
    await message.answer("Привет! Я работаю на aiogram 3.x!")

# Функция main() должна быть объявлена перед вызовом asyncio.run()
async def main():
    print("Бот запущен...")  # Лог для проверки работы бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
