from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_after_spread_buttons() -> InlineKeyboardMarkup:
    """Buttons after spread (inline)"""
    buttons = [
        [
            InlineKeyboardButton(text="🔄 НОВЫЙ РАСКЛАД", callback_data="new_spread"),
            InlineKeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ", callback_data="menu:main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)