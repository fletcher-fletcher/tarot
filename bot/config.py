import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Telegram
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_USERNAME = os.getenv("BOT_USERNAME", "tarot_bot")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/tarot_bot.db")
    
    # Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    STATIC_DIR = BASE_DIR / "bot" / "static"
    CARDS_DIR = STATIC_DIR / "tarot_cards"
    BACKGROUNDS_DIR = STATIC_DIR / "backgrounds"
    FONTS_DIR = STATIC_DIR / "fonts"
    TEMP_DIR = BASE_DIR / "temp"
    
    # Create directories if not exist
    DATA_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    CARDS_DIR.mkdir(exist_ok=True)
    BACKGROUNDS_DIR.mkdir(exist_ok=True)
    FONTS_DIR.mkdir(exist_ok=True)
    
    # User settings defaults
    DEFAULT_SHOW_IMAGES = True
    DEFAULT_SHOW_REVERSED = True
    DEFAULT_DAILY_CARD_TIME = "09:00"
    DEFAULT_TIMEZONE = "Europe/Moscow"
    DEFAULT_NOTIFICATIONS_ENABLED = True
    
    # History
    MAX_HISTORY_SIZE = 20
    
    # Timezones list for selection
    TIMEZONES = [
        ("Europe/Moscow", "МСК (Москва)"),
        ("Europe/Kaliningrad", "Калининград (UTC+2)"),
        ("Europe/Samara", "Самара (UTC+4)"),
        ("Asia/Yekaterinburg", "Екатеринбург (UTC+5)"),
        ("Asia/Omsk", "Омск (UTC+6)"),
        ("Asia/Krasnoyarsk", "Красноярск (UTC+7)"),
        ("Asia/Irkutsk", "Иркутск (UTC+8)"),
        ("Asia/Yakutsk", "Якутск (UTC+9)"),
        ("Asia/Vladivostok", "Владивосток (UTC+10)"),
        ("Asia/Magadan", "Магадан (UTC+11)"),
        ("Asia/Kamchatka", "Камчатка (UTC+12)"),
        ("UTC", "UTC"),
        ("Europe/London", "Лондон"),
        ("America/New_York", "Нью-Йорк"),
        ("Asia/Tokyo", "Токио"),
    ]


settings = Settings()