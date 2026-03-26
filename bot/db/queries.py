from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User, History
from bot.config import settings


# ==================== USER ====================

async def get_user(session: AsyncSession, telegram_id: int) -> Optional[User]:
    """Get user by telegram_id"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None
) -> User:
    """Create new user"""
    import json
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        usage_today=json.dumps({"card_day": 0, "categories": 0}),  # <-- ВАЖНО: сериализуем в JSON строку
        last_reset_date=datetime.utcnow()
    )
    session.add(user)
    await session.flush()
    return user


async def update_user(
    session: AsyncSession,
    telegram_id: int,
    **kwargs
) -> Optional[User]:
    """Update user data"""
    user = await get_user(session, telegram_id)
    if not user:
        return None
    
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    await session.flush()
    return user


async def update_settings(
    session: AsyncSession,
    telegram_id: int,
    show_images: Optional[bool] = None,
    show_reversed: Optional[bool] = None,
    daily_card_time: Optional[str] = None,
    timezone: Optional[str] = None,
    notifications_enabled: Optional[bool] = None
) -> Optional[User]:
    """Update user settings"""
    user = await get_user(session, telegram_id)
    if not user:
        return None
    
    if show_images is not None:
        user.show_images = show_images
    if show_reversed is not None:
        user.show_reversed = show_reversed
    if daily_card_time is not None:
        user.daily_card_time = daily_card_time
    if timezone is not None:
        user.timezone = timezone
    if notifications_enabled is not None:
        user.notifications_enabled = notifications_enabled
    
    user.updated_at = datetime.utcnow()
    await session.flush()
    return user


async def get_all_users_with_notifications(session: AsyncSession) -> List[User]:
    """Get all users with notifications enabled"""
    result = await session.execute(
        select(User).where(User.notifications_enabled == True)
    )
    return result.scalars().all()


# ==================== HISTORY ====================

async def save_spread(
    session: AsyncSession,
    user_id: int,
    spread_type: str,
    spread_data: List[Dict[str, Any]],
    question: Optional[str] = None,
    image_path: Optional[str] = None
) -> History:
    """Save spread to history"""
    history = History(
        user_id=user_id,
        spread_type=spread_type,
        spread_data=spread_data,
        question=question,
        image_path=image_path
    )
    session.add(history)
    await session.flush()
    
    # Limit history size
    result = await session.execute(
        select(History)
        .where(History.user_id == user_id)
        .order_by(desc(History.created_at))
    )
    all_history = result.scalars().all()
    
    if len(all_history) > settings.MAX_HISTORY_SIZE:
        to_delete = all_history[settings.MAX_HISTORY_SIZE:]
        for item in to_delete:
            await session.delete(item)
    
    return history


async def get_user_history(
    session: AsyncSession,
    user_id: int,
    limit: int = 10
) -> List[History]:
    """Get user's recent spreads"""
    result = await session.execute(
        select(History)
        .where(History.user_id == user_id)
        .order_by(desc(History.created_at))
        .limit(limit)
    )
    return result.scalars().all()


async def clear_history(
    session: AsyncSession,
    user_id: int
) -> int:
    """Clear user's history"""
    result = await session.execute(
        select(History).where(History.user_id == user_id)
    )
    history = result.scalars().all()
    
    count = len(history)
    for item in history:
        await session.delete(item)
    
    return count


async def update_daily_usage(
    session: AsyncSession,
    user_id: int,
    spread_type: str
) -> None:
    """Update daily usage counter"""
    user = await get_user(session, user_id)
    if not user:
        return
    
    today = datetime.utcnow().date()
    last_reset = user.last_reset_date.date() if user.last_reset_date else None
    
    if last_reset != today:
        user.usage_today = {"card_day": 0, "categories": 0}
        user.last_reset_date = datetime.utcnow()
    
    user.usage_today[spread_type] = user.usage_today.get(spread_type, 0) + 1
    await session.commit()