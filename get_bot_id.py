import asyncio
from aiogram import Bot
from bot.config import settings

async def get_bot_info():
    """Get bot information"""
    bot = Bot(token=settings.BOT_TOKEN)
    
    try:
        # Получаем информацию о боте
        me = await bot.get_me()
        
        print("=== BOT INFORMATION ===")
        print(f"Bot ID: {me.id}")
        print(f"Bot username: @{me.username}")
        print(f"Bot first name: {me.first_name}")
        print(f"Is bot: {me.is_bot}")
        
        # Получаем обновления, чтобы увидеть последние сообщения
        updates = await bot.get_updates(limit=1)
        
        if updates:
            print("\n=== LAST MESSAGE ===")
            last_update = updates[-1]
            if last_update.message:
                msg = last_update.message
                print(f"From user ID: {msg.from_user.id}")
                print(f"From username: @{msg.from_user.username}")
                print(f"From first name: {msg.from_user.first_name}")
                print(f"Is bot: {msg.from_user.is_bot}")
                print(f"Chat ID: {msg.chat.id}")
                print(f"Message text: {msg.text}")
        
        await bot.session.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_bot_info())