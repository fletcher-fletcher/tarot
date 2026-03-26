import asyncio
from bot.db import get_session, get_user
from bot.db.database import engine
from sqlalchemy import text

async def check_database():
    telegram_id = 8678409339
    
    print("=== CHECKING DATABASE ===")
    
    # Проверяем подключение
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(f"Database connection: OK")
    
    # Получаем пользователя
    async with get_session() as session:
        user = await get_user(session, telegram_id)
        if user:
            print(f"\nUser found:")
            print(f"  telegram_id: {user.telegram_id}")
            print(f"  usage_today: {user.usage_today}")
            print(f"  last_reset_date: {user.last_reset_date}")
            print(f"  created_at: {user.created_at}")
        else:
            print(f"\nUser {telegram_id} NOT found in database")
        
        # Проверяем все записи в таблице users
        print("\n=== ALL USERS ===")
        from sqlalchemy import select
        from bot.db.models import User
        result = await session.execute(select(User))
        all_users = result.scalars().all()
        for u in all_users:
            print(f"User {u.telegram_id}: usage={u.usage_today}")

if __name__ == "__main__":
    asyncio.run(check_database())