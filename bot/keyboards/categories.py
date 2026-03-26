from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.scenarios import CATEGORIES, SUBCATEGORIES, PROBLEMS
import re


def get_main_category_menu() -> InlineKeyboardMarkup:
    """Level 1: Main categories menu"""
    buttons = []
    for code, name in CATEGORIES.items():
        # Обрезаем название категории (обычно и так короткое)
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"cat:{code}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subcategory_menu(category_code: str) -> InlineKeyboardMarkup:
    """Level 2: Subcategories menu for selected category"""
    subcats = SUBCATEGORIES.get(category_code, {})
    
    buttons = []
    for code, name in subcats.items():
        # Обрезаем название подкатегории
        if len(name) > 45:
            name = name[:42] + "..."
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"sub:{category_code}:{code}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 НАЗАД", callback_data="back_to_categories")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_problem_menu(category_code: str, subcategory_code: str) -> InlineKeyboardMarkup:
    """Level 3: Problems menu for selected subcategory"""
    problems = PROBLEMS.get(category_code, {}).get(subcategory_code, [])
    
    buttons = []
    for problem in problems[:12]:
        text = problem["text"]
        # Удаляем эмодзи для экономии места
        text = re.sub(r'[💔🤔💭💑🤝💍🔐📍💔👨‍👩‍👧🔥👤🔄🤝🚧🔥🚪🌱⚔️👔🤔🏢⚖️📄💻🏆💰👥📈🎯💪🌑⏳🕊️🙏😤🌙😞😤🤔🦋🚪✨❤️🌊🦁🕯️👨‍👩‍👧👶🏡🚪🔄📦💥⚖️👫🎄🧓🏠🏠🕯️⚡😴😰🌿⚖️🧘🍎🧠🛡️⚖️🌱🌀📆🤕🛡️🔥]', '', text)
        # Обрезаем до 45 символов
        if len(text) > 45:
            text = text[:42] + "..."
        buttons.append([InlineKeyboardButton(
            text=text,
            callback_data=f"prob:{category_code}:{subcategory_code}:{problem['code']}"
        )])
    
    buttons.append([InlineKeyboardButton(text="🔙 НАЗАД", callback_data=f"back_to_sub:{category_code}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)