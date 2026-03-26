import asyncio
from sqlalchemy import text
from bot.db.database import engine

async def check_json():
    async with engine.connect() as conn:
        # Проверяем структуру таблицы
        result = await conn.execute(text("PRAGMA table_info(users)"))
        columns = result.fetchall()
        print("Table structure:")
        for col in columns:
            print(f"  {col[1]}: {col[2]}")
        
        # Проверяем данные
        result = await conn.execute(text("SELECT telegram_id, usage_today FROM users"))
        rows = result.fetchall()
        print("\nUser data:")
        for row in rows:
            print(f"  User {row[0]}: usage_today={row[1]} (type={type(row[1])})")

if __name__ == "__main__":
    asyncio.run(check_json())