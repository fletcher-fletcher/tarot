"""Daily limits for users"""

from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import json

from bot.db.queries import get_user


DAILY_LIMITS = {
    "card_day": 1,      # 1 карта дня в день
    "categories": 3,    # 3 любых расклада в день
}


def parse_usage(usage):
    """Parse usage from string or dict"""
    if isinstance(usage, str):
        return json.loads(usage)
    return usage or {"card_day": 0, "categories": 0}


def serialize_usage(usage):
    """Serialize usage to string"""
    return json.dumps(usage)


async def check_and_update_limit(
    session: AsyncSession,
    telegram_id: int,
    spread_type: str
) -> tuple[bool, int, int]:
    """
    Check limit and increment counter.
    Returns: (can_do, used_today, limit)
    """
    logger.info(f"🔍 CHECKING LIMIT: user={telegram_id}, type={spread_type}")
    
    # Получаем пользователя
    user = await get_user(session, telegram_id)
    if not user:
        logger.info(f"⚠️ User {telegram_id} not found, allowing")
        return True, 0, DAILY_LIMITS.get(spread_type, 999)
    
    # Парсим usage_today
    usage = parse_usage(user.usage_today)
    
    # Check if limits need reset (new day)
    last_reset = user.last_reset_date.date() if user.last_reset_date else None
    today = date.today()
    
    logger.info(f"📅 Last reset: {last_reset}, Today: {today}")
    
    if last_reset != today:
        # Сброс лимитов
        usage = {"card_day": 0, "categories": 0}
        user.last_reset_date = datetime.utcnow()
        user.usage_today = serialize_usage(usage)
        await session.commit()
        logger.info(f"🔄 Reset limits for user {telegram_id}")
        logger.info(f"📊 After reset: usage={usage}")
    
    # Get current usage
    used = usage.get(spread_type, 0)
    limit = DAILY_LIMITS.get(spread_type, 999)
    
    logger.info(f"📊 User {telegram_id} - {spread_type}: used={used}, limit={limit}")
    logger.info(f"📊 Full usage: {usage}")
    
    # Check
    if used >= limit:
        logger.warning(f"❌ LIMIT EXCEEDED: user={telegram_id}, used={used}, limit={limit}")
        return False, used, limit
    
    # Increment counter
    usage[spread_type] = used + 1
    user.usage_today = serialize_usage(usage)
    logger.info(f"✏️ Setting {spread_type} to {used + 1}")
    logger.info(f"✏️ Full usage before commit: {usage}")
    
    # Принудительно коммитим
    await session.commit()
    logger.info(f"✅ Commit done")
    
    # Проверяем
    await session.refresh(user)
    saved_usage = parse_usage(user.usage_today)
    logger.info(f"✅ After refresh: usage={saved_usage}")
    logger.info(f"✅ INCREMENTED: user={telegram_id}, {spread_type} now={saved_usage.get(spread_type)}")
    
    return True, used + 1, limit


async def get_remaining_limits(
    session: AsyncSession,
    telegram_id: int
) -> dict:
    """
    Get remaining limits for all spread types.
    Returns: dict with remaining counts
    """
    user = await get_user(session, telegram_id)
    if not user:
        return {
            "card_day": DAILY_LIMITS.get("card_day", 1),
            "categories": DAILY_LIMITS.get("categories", 3)
        }
    
    # Парсим usage_today
    usage = parse_usage(user.usage_today)
    
    # Check if limits need reset (new day)
    last_reset = user.last_reset_date.date() if user.last_reset_date else None
    today = date.today()
    
    if last_reset != today:
        # Reset limits
        usage = {"card_day": 0, "categories": 0}
        user.usage_today = serialize_usage(usage)
        user.last_reset_date = datetime.utcnow()
        await session.commit()
        logger.debug(f"Reset limits for user {telegram_id} in get_remaining_limits")
    
    # Calculate remaining
    remaining = {}
    for spread_type, limit in DAILY_LIMITS.items():
        used = usage.get(spread_type, 0)
        remaining[spread_type] = max(0, limit - used)
    
    return remaining