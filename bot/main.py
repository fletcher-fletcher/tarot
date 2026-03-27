import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from loguru import logger
from bot.handlers.admin import router as admin_router

from bot.config import settings
from bot.handlers import (
    start_router,
    card_day_menu_router,
    categories_router,
    settings_router,
)

# Initialize bot
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Initialize dispatcher
dp = Dispatcher()

# Register routers
dp.include_router(start_router)
dp.include_router(card_day_menu_router)
dp.include_router(categories_router)
dp.include_router(settings_router)
dp.include_router(admin_router)


async def main():
    """Main entry point"""
    logger.info(f"Starting bot: @{settings.BOT_USERNAME}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
