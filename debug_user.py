import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from loguru import logger

# Настройка логирования
import logging
logging.basicConfig(level=logging.INFO)

# Токен бота (используем ваш из конфига)
from bot.config import settings

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Detailed user info"""
    # Подробная информация
    info = f"""
🔍 <b>ДЕТАЛЬНАЯ ИНФОРМАЦИЯ</b>

<b>message.from_user:</b>
├─ id: <code>{message.from_user.id}</code>
├─ is_bot: {message.from_user.is_bot}
├─ username: @{message.from_user.username}
├─ first_name: {message.from_user.first_name}
└─ last_name: {message.from_user.last_name}

<b>message.chat:</b>
├─ id: <code>{message.chat.id}</code>
├─ type: {message.chat.type}
├─ username: @{message.chat.username}
└─ title: {message.chat.title}

<b>message:</b>
├─ message_id: {message.message_id}
└─ date: {message.date}
    """
    
    # Выводим в консоль
    logger.info(f"User ID from message: {message.from_user.id}")
    logger.info(f"Chat ID: {message.chat.id}")
    logger.info(f"Is bot: {message.from_user.is_bot}")
    
    # Отправляем ответ пользователю
    await message.answer(info, parse_mode="HTML")

@dp.message()
async def echo(message: types.Message):
    """Echo any message with info"""
    await message.answer(
        f"Ваш ID: <code>{message.from_user.id}</code>\n"
        f"Это {'бот' if message.from_user.is_bot else 'пользователь'}",
        parse_mode="HTML"
    )

async def main():
    print("🚀 Бот запущен для отладки...")
    print(f"Бот ID: {bot.id}")
    print("Напишите /start или любое сообщение")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())