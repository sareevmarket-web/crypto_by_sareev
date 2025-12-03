import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import signals
from database import add_signal

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# СЮДА ВСТАВЬ СВОИ ДАННЫЕ (две строчки!)
BOT_TOKEN = "7766540110:AAGmeV7dnsswnxTbFMw_8z5jMO1fFVq5hqM"  # ← твой токен
MY_ID     = 304069115                                        # ← твой ID
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id != MY_ID:
        await message.answer("Доступ запрещён")
        return
    await message.answer(
        "Бот сигналов запущен!\n\n"
        "Сигналы приходят автоматически каждые 30 минут.\n"
        "Напиши /now — проверить прямо сейчас"
    )

@dp.message(Command("now"))
async def cmd_now(message: Message):
    if message.from_user.id != MY_ID:
        return
    await message.answer("Смотрю рынок...")
    found = signals.find_signals()

    if not found:
        await message.answer("Пока сильных сигналов нет")
        return

    for s in found:
        text = f"""
{S['symbol']} — {s['direction']} {s['leverage']}x

Цена входа: ${s['price']}
Стоп-лосс:   ${s['sl']}
Тейк-профит: ${s['tp']}
Сентимент: {s['sentiment']}
        """.strip()
        await bot.send_message(MY_ID, text)
        # Сохраняем в базу
        add_signal(s['symbol'], s['direction'], s['price'], s['sl'], s['tp'], s['leverage'])

# Фоновая задача — проверяет каждые 30 минут
async def auto_check():
    while True:
        found = signals.find_signals()
        for s in found:
            text = f"AUTO {s['symbol']} {s['direction']} {s['leverage']}x\n${s['price']} → TP ${s['tp']}"
            await bot.send_message(MY_ID, text)
            add_signal(s['symbol'], s['direction'], s['price'], s['sl'], s['tp'], s['leverage'])
        await asyncio.sleep(1800)  # 30 минут

async def main():
    # Запускаем авто-проверку в фоне
    asyncio.create_task(auto_check())
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())
    
