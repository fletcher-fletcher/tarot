from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard"""
    buttons = [
        [KeyboardButton(text="🎴 КАРТА ДНЯ")],
        [KeyboardButton(text="🔮 РАСКЛАДЫ")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )