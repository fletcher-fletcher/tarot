from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import settings


def get_settings_menu(show_images: bool, show_reversed: bool, notifications: bool, time: str, timezone: str) -> InlineKeyboardMarkup:
    """Settings menu"""
    images_status = "✅ ВКЛ" if show_images else "❌ ВЫКЛ"
    reversed_status = "✅ ВКЛ" if show_reversed else "❌ ВЫКЛ"
    notifications_status = "✅ ВКЛ" if notifications else "❌ ВЫКЛ"
    
    # Find timezone display name
    tz_name = timezone
    for tz_code, tz_display in settings.TIMEZONES:
        if tz_code == timezone:
            tz_name = tz_display
            break
    
    buttons = [
        [InlineKeyboardButton(text=f"⏰ ВРЕМЯ КАРТЫ ДНЯ: {time}", callback_data="setting:set_time")],
        [InlineKeyboardButton(text=f"🌍 ЧАСОВОЙ ПОЯС: {tz_name}", callback_data="setting:set_timezone")],
        [InlineKeyboardButton(text="🔙 НАЗАД", callback_data="menu:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_time_menu() -> InlineKeyboardMarkup:
    """Time selection menu"""
    buttons = [
        [InlineKeyboardButton(text="🕐 07:00", callback_data="time:07:00")],
        [InlineKeyboardButton(text="🕑 08:00", callback_data="time:08:00")],
        [InlineKeyboardButton(text="🕒 09:00", callback_data="time:09:00")],
        [InlineKeyboardButton(text="🕓 10:00", callback_data="time:10:00")],
        [InlineKeyboardButton(text="🕔 11:00", callback_data="time:11:00")],
        [InlineKeyboardButton(text="🕕 12:00", callback_data="time:12:00")],
        [InlineKeyboardButton(text="🕖 18:00", callback_data="time:18:00")],
        [InlineKeyboardButton(text="🕗 19:00", callback_data="time:19:00")],
        [InlineKeyboardButton(text="🕘 20:00", callback_data="time:20:00")],
        [InlineKeyboardButton(text="🔙 НАЗАД", callback_data="settings:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_timezone_menu() -> InlineKeyboardMarkup:
    """Timezone selection menu"""
    buttons = []
    for tz_code, tz_name in settings.TIMEZONES:
        buttons.append([InlineKeyboardButton(text=tz_name, callback_data=f"tz:{tz_code}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 НАЗАД", callback_data="settings:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)