import asyncio
import json
import os
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

# 🔹 Включаем логи для отладки
logging.basicConfig(level=logging.INFO)

# 🔹 Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_PROVIDER = os.getenv("TELEGRAM_PAY_TOKEN")

# 🔹 Подключение к Google Sheets
SERVICE_ACCOUNT_FILE = "sfybot-03184c7b622d.json"
SHEET_ID = "19i-_I-DMeFSA3tNCgpm5P90y_PZfAcICkYy0Qq1wT0U"

def get_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1  # Открываем первый лист
    return sheet

# 🔹 Получение подписок из Google Sheets
def load_subscriptions():
    sheet = get_google_sheet()
    data = sheet.get_all_records()
    subscriptions = {}
    
    for row in data:
        sub_id = row["ID подписки"]
        subscriptions[sub_id] = {
            "name": row["Название"],
            "price": int(row["Цена"] * 100),  # Конвертируем в копейки
            "status": row["Статус"],
            "buyer": row.get("Покупатель", "")
        }
    return subscriptions

# 🔹 Обновление подписки после покупки
def update_subscription(sub_id, buyer_id):
    sheet = get_google_sheet()
    data = sheet.get_all_records()

    print(f"Обновляем подписку {sub_id}: статус 'Выкуплено', покупатель {buyer_id}")  # 🔹 Отладка

    for i, row in enumerate(data, start=2):
        if row["ID подписки"] == sub_id:
            sheet.update(f"D{i}", "Выкуплено")  # Убедись, что 'D' — это "Статус"
            sheet.update(f"E{i}", str(buyer_id))  # Убедись, что 'E' — это "Покупатель"
            break

# 🔹 Создаем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# 🔹 Обработчик команды /start
@router.message(Command("start"))
async def start(message: types.Message):
    subscriptions = load_subscriptions()
    text = "👋 Привет! Выбери подписку из списка ниже:" 

    keyboard = InlineKeyboardBuilder()
    for sub_id, sub in subscriptions.items():
        if sub["status"].lower() != "выкуплено":
            keyboard.button(text=f"{sub['name']} — {sub['price'] / 100} руб.", callback_data=str(sub_id))
    
    keyboard.adjust(1)
    await message.answer(text, reply_markup=keyboard.as_markup())

# 🔹 Обработчик покупки
@router.callback_query()
async def process_callback(callback: types.CallbackQuery):
    subscriptions = load_subscriptions()
    sub_id = callback.data

    if sub_id not in subscriptions or subscriptions[sub_id]["status"].lower() == "выкуплено":
        await callback.answer("❌ Подписка уже выкуплена или не найдена.", show_alert=True)
        return

    sub = subscriptions[sub_id]
    prices = [LabeledPrice(label=sub["name"], amount=sub["price"])]

    await bot.send_invoice(
        callback.from_user.id,
        title=sub["name"],
        description=f"Вы покупаете {sub['name']}",
        payload=sub_id,
        provider_token=PAYMENT_PROVIDER,
        currency="RUB",
        prices=prices
    )
    await callback.answer()

# 🔹 Подтверждение оплаты
@router.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# 🔹 Обработчик успешной оплаты
@router.message(F.successful_payment)
async def successful_payment(message: types.Message):
    sub_id = message.successful_payment.invoice_payload
    buyer_id = message.from_user.id
    update_subscription(sub_id, buyer_id)
    await message.answer("✅ Оплата прошла успешно! Подписка активирована.")

# Запуск бота
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
