from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_card_day_menu() -> InlineKeyboardMarkup:
    """Menu for card of the day"""
    buttons = [
        [InlineKeyboardButton(text="🎴 ПОЛУЧИТЬ КАРТУ ДНЯ", callback_data="card_day:get")],
        [InlineKeyboardButton(text="⚙️ НАСТРОЙКИ КАРТЫ ДНЯ", callback_data="card_day:settings")],
        [InlineKeyboardButton(text="🔙 ГЛАВНОЕ МЕНЮ", callback_data="menu:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_card_day_time_menu() -> InlineKeyboardMarkup:
    """Time and timezone settings for card day"""
    buttons = [
        [InlineKeyboardButton(text="⏰ ВРЕМЯ ОТПРАВКИ", callback_data="card_day:set_time")],
        [InlineKeyboardButton(text="🌍 ЧАСОВОЙ ПОЯС", callback_data="card_day:set_timezone")],
        [InlineKeyboardButton(text="🔙 НАЗАД", callback_data="card_day:menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)