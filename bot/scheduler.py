"""Scheduler for daily card delivery"""

import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
import pytz

from bot.config import settings
from bot.db import get_session, get_all_users_with_notifications, get_user
from bot.core.deck import get_random_card, get_card_by_id
from bot.services.groq import generate_tarot_reading
from bot.utils.helpers import get_current_time_in_timezone

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def send_daily_card():
    """Send daily card to all users"""
    logger.info("Sending daily cards...")
    
    async with get_session() as session:
        users = await get_all_users_with_notifications(session)
        
        for user in users:
            try:
                # Get user's time
                user_time = get_current_time_in_timezone(user.timezone)
                current_hour = user_time.strftime("%H:%M")
                
                # Check if it's time to send
                if current_hour != user.daily_card_time:
                    continue
                
                # Draw card
                card_id = get_random_card().card_id
                card = get_card_by_id(card_id)
                card.is_reversed = False
                
                # Generate reading
                reading = await generate_tarot_reading(
                    scenario_name="Карта дня",
                    problem_text="Ежедневная карта-совет",
                    cards=[card],
                    spread_type="one_card"
                )
                
                # Format message
                text = f"🌅 <b>ДОБРОЕ УТРО!</b>\n\n"
                text += f"🃏 <b>{card.name_ru}</b>\n\n"
                text += f"{reading}"
                
                # Send via bot (import here to avoid circular import)
                from bot.main import bot
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=text,
                    parse_mode="HTML"
                )
                
                logger.info(f"Daily card sent to user {user.telegram_id}")
                
            except Exception as e:
                logger.error(f"Failed to send daily card to {user.telegram_id}: {e}")
                continue


async def start_scheduler():
    """Start the scheduler"""
    # Run every minute to check times
    scheduler.add_job(
        send_daily_card,
        trigger=CronTrigger(minute="*"),
        id="daily_card_job"
    )
    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")