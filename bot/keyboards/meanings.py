from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_meanings_menu() -> InlineKeyboardMarkup:
    """Meanings menu"""
    buttons = [
        [InlineKeyboardButton(text="👑 СТАРШИЕ АРКАНЫ", callback_data="meanings:major")],
        [InlineKeyboardButton(text="🔥 МЛАДШИЕ АРКАНЫ", callback_data="meanings:minor")],
        [InlineKeyboardButton(text="🔙 НАЗАД", callback_data="menu:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_arcana_menu() -> InlineKeyboardMarkup:
    """Major arcana selection menu"""
    major_cards = [
        ("0 Дурак", "major:00_fool"),
        ("1 Маг", "major:01_magician"),
        ("2 Верховная Жрица", "major:02_high_priestess"),
        ("3 Императрица", "major:03_empress"),
        ("4 Император", "major:04_emperor"),
        ("5 Иерофант", "major:05_hierophant"),
        ("6 Влюблённые", "major:06_lovers"),
        ("7 Колесница", "major:07_chariot"),
        ("8 Сила", "major:08_strength"),
        ("9 Отшельник", "major:09_hermit"),
        ("10 Колесо Фортуны", "major:10_wheel_of_fortune"),
        ("11 Справедливость", "major:11_justice"),
        ("12 Повешенный", "major:12_hanged_man"),
        ("13 Смерть", "major:13_death"),
        ("14 Умеренность", "major:14_temperance"),
        ("15 Дьявол", "major:15_devil"),
        ("16 Башня", "major:16_tower"),
        ("17 Звезда", "major:17_star"),
        ("18 Луна", "major:18_moon"),
        ("19 Солнце", "major:19_sun"),
        ("20 Суд", "major:20_judgement"),
        ("21 Мир", "major:21_world"),
    ]
    
    buttons = []
    row = []
    for name, callback in major_cards:
        row.append(InlineKeyboardButton(text=name, callback_data=callback))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="🔙 НАЗАД", callback_data="meanings:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_suit_menu() -> InlineKeyboardMarkup:
    """Minor arcana suit selection menu"""
    buttons = [
        [InlineKeyboardButton(text="🪄 ЖЕЗЛЫ (Огонь)", callback_data="suit:wands")],
        [InlineKeyboardButton(text="💧 КУБКИ (Вода)", callback_data="suit:cups")],
        [InlineKeyboardButton(text="⚔️ МЕЧИ (Воздух)", callback_data="suit:swords")],
        [InlineKeyboardButton(text="🪙 ПЕНТАКЛИ (Земля)", callback_data="suit:pentacles")],
        [InlineKeyboardButton(text="🔙 НАЗАД", callback_data="meanings:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)