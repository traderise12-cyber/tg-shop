import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery, Message
from aiohttp import web

# Настройки твоего бота
API_TOKEN = '8919058903:AAFftDvkOk-h7yu7UOih7tpq-HrcTN04bxk'
ADMIN_ID = 6523793120
WEBAPP_URL = 'https://traderise12-cyber.github.io/tg-shop/'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Заглушка-сервер, чтобы бесплатный тариф Render не отключал бота
async def handle(request):
    return web.Response(text="Бот активен и работает!")

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton(text="🔑 Панель Администратора", web_app=WebAppInfo(url=f"{WEBAPP_URL}?role=admin"))]
        ])
        await message.answer("Привет, Создатель! Магазин готов к работе.", reply_markup=kb)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))]
        ])
        await message.answer("Привет! Нажми на кнопку ниже, чтобы открыть наш магазин.", reply_markup=kb)

@dp.message(F.web_app_data)
async def web_app_payment_request(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get("action") == "order":
            item_name = data.get("item")
            stars_price = int(data.get("cost")) 
            prices = [LabeledPrice(label=item_name, amount=stars_price)]
            
            await bot.send_invoice(
                chat_id=message.chat.id,
                title=f"Покупка: {item_name}",
                description=f"Оплата товара внутри мини-приложения",
                payload=f"payload_{item_name}",
                provider_token="", 
                currency="XTR",    
                prices=prices
            )
    except Exception as e:
        await message.answer(f"🔴 Ошибка генерации счёта: {e}")

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payment_info = message.successful_payment
    product_name = payment_info.invoice_payload.replace("payload_", "")
    await message.answer(f"🎉 **Товар успешно оплачен!**\n\n📦 Предмет: {product_name}\n💸 Списано: {payment_info.total_amount} ⭐️")

async def main():
    # Запуск веб-сервера для Render параллельно с ботом
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Порт, который требует Render
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    asyncio.create_task(site.start())
    
    print("🚀 Бот и веб-сервер успешно запущены!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
