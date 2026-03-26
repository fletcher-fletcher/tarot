from bot.handlers.start import router as start_router
from bot.handlers.card_day_menu import router as card_day_menu_router
from bot.handlers.categories import router as categories_router
from bot.handlers.settings import router as settings_router

__all__ = [
    "start_router",
    "card_day_menu_router",
    "categories_router",
    "settings_router",
]