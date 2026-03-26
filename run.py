#!/usr/bin/env python3
"""Main entry point for the bot"""

import asyncio
import sys
import os
from pathlib import Path
from loguru import logger

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bot.db.database import init_db
from bot.scheduler import start_scheduler, stop_scheduler
from bot.config import settings


# Для веб-сервера (health check)
try:
    from aiohttp import web
except ImportError:
    web = None
    logger.warning("aiohttp not installed, web server disabled")


async def health_check(request):
    """Health check endpoint for Render"""
    return web.Response(text="OK", status=200)


async def start_web_server():
    """Start web server for health checks and cron jobs"""
    if not web:
        logger.warning("Web server not started: aiohttp not installed")
        return
    
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    
    # Можно добавить эндпоинт для ручного триггера (защитите токеном)
    async def trigger_daily_card(request):
        """Manual trigger for daily card (protected by token)"""
        token = request.query.get('token')
        if token != os.getenv("WEBHOOK_TOKEN", ""):
            return web.Response(text="Unauthorized", status=401)
        
        # Запускаем отправку карт дня
        from bot.scheduler import send_daily_card
        asyncio.create_task(send_daily_card())
        return web.Response(text="Daily card triggered", status=200)
    
    app.router.add_get('/trigger/daily', trigger_daily_card)
    
    # Получаем порт из переменной окружения (Render даёт PORT=10000)
    port = int(os.getenv("PORT", 10000))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"Web server started on port {port}")
    logger.info(f"Health check: http://0.0.0.0:{port}/health")
    logger.info(f"Trigger daily (with token): http://0.0.0.0:{port}/trigger/daily?token=YOUR_TOKEN")


async def main():
    """Main function"""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    
    logger.info("Starting scheduler...")
    await start_scheduler()
    
    logger.info("Starting web server...")
    # Запускаем веб-сервер в фоне
    asyncio.create_task(start_web_server())
    
    logger.info(f"Starting bot: @{settings.BOT_USERNAME}")
    
    # Импортируем бота здесь, чтобы избежать циклических импортов
    from bot.main import main as bot_main
    await bot_main()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
        stop_scheduler()
        logger.info("Goodbye!")
