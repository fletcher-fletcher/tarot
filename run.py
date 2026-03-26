#!/usr/bin/env python3
import sys
import asyncio
from loguru import logger

from bot.config import settings
from bot.db.database import init_db
from bot.utils.logger import setup_logger
from bot.scheduler import start_scheduler, stop_scheduler


async def main():
    """Run the bot"""
    # Setup logging
    setup_logger()
    
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    
    # Start scheduler for daily card
    logger.info("Starting scheduler...")
    await start_scheduler()
    
    # Import and run bot
    from bot.main import main as bot_main
    await bot_main()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        stop_scheduler()
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)