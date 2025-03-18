import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from aiogram import Bot, Dispatcher, types
import asyncio

# Загружаем JSON-ключ из переменной окружения
google_credentials = json.loads(os.getenv("GOOGLE_CREDENTIALS"))

# Авторизация в Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_credentials, scope)

# Инициализация бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Бот успешно запущен! ✅")

if __name__ == "__main__":
    asyncio.run(main())


async def main():
    await dp.start_polling(bot)
