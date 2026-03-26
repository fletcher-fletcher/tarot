from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.settings import get_settings_menu, get_time_menu, get_timezone_menu
from bot.keyboards.main import get_main_keyboard
from bot.config import settings
from bot.db import get_session, get_user, update_settings

router = Router()


class SettingsStates(StatesGroup):
    waiting_for_time = State()
    waiting_for_timezone = State()


@router.message(Command("settings"))
@router.message(lambda msg: msg.text == "⚙️ НАСТРОЙКИ")
async def show_settings(message: Message):
    """Show settings menu"""
    async with get_session() as session:
        user = await get_user(session, message.from_user.id)
        if not user:
            await message.answer("❌ Ошибка: пользователь не найден")
            return
        
        await message.answer(
            "⚙️ <b>Настройки карты дня</b>\n\n"
            "Настройте время и часовой пояс:",
            reply_markup=get_settings_menu(
                show_images=user.show_images,
                show_reversed=user.show_reversed,
                notifications=user.notifications_enabled,
                time=user.daily_card_time,
                timezone=user.timezone
            ),
            parse_mode="HTML"
        )


@router.callback_query(lambda c: c.data.startswith("setting:"))
async def handle_settings(callback: CallbackQuery, state: FSMContext):
    """Handle settings actions"""
    action = callback.data.split(":")[1]
    
    async with get_session() as session:
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.message.answer("❌ Ошибка: пользователь не найден")
            await callback.answer()
            return
        
        if action == "set_time":
            await callback.message.edit_text(
                "⏰ <b>Время карты дня</b>\n\n"
                "Выберите время для ежедневной рассылки:",
                reply_markup=get_time_menu(),
                parse_mode="HTML"
            )
        
        elif action == "set_timezone":
            await callback.message.edit_text(
                "🌍 <b>Часовой пояс</b>\n\n"
                "Выберите ваш часовой пояс:",
                reply_markup=get_timezone_menu(),
                parse_mode="HTML"
            )
    
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("time:"))
async def set_time(callback: CallbackQuery):
    """Set daily card time"""
    time_str = callback.data.split(":")[1]
    
    async with get_session() as session:
        await update_settings(session, callback.from_user.id, daily_card_time=time_str)
        
        user = await get_user(session, callback.from_user.id)
        
        await callback.message.edit_text(
            f"⏰ <b>Время установлено</b>\n\n"
            f"Карта дня будет приходить каждый день в <b>{time_str}</b> "
            f"по вашему часовому поясу.\n\n"
            f"Не забудьте включить уведомления в настройках Telegram!",
            parse_mode="HTML",
            reply_markup=get_settings_menu(
                show_images=user.show_images,
                show_reversed=user.show_reversed,
                notifications=user.notifications_enabled,
                time=user.daily_card_time,
                timezone=user.timezone
            )
        )
    
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("tz:"))
async def set_timezone(callback: CallbackQuery):
    """Set timezone"""
    tz_code = callback.data.split(":")[1]
    
    async with get_session() as session:
        await update_settings(session, callback.from_user.id, timezone=tz_code)
        
        user = await get_user(session, callback.from_user.id)
        
        await callback.message.edit_text(
            f"🌍 <b>Часовой пояс установлен</b>\n\n"
            f"Карта дня будет приходить в {user.daily_card_time} по вашему времени.",
            parse_mode="HTML",
            reply_markup=get_settings_menu(
                show_images=user.show_images,
                show_reversed=user.show_reversed,
                notifications=user.notifications_enabled,
                time=user.daily_card_time,
                timezone=user.timezone
            )
        )
    
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings:main")
async def back_to_settings(callback: CallbackQuery):
    """Back to settings main"""
    async with get_session() as session:
        user = await get_user(session, callback.from_user.id)
        if user:
            await callback.message.edit_text(
                "⚙️ <b>Настройки карты дня</b>\n\n"
                "Настройте время и часовой пояс:",
                reply_markup=get_settings_menu(
                    show_images=user.show_images,
                    show_reversed=user.show_reversed,
                    notifications=user.notifications_enabled,
                    time=user.daily_card_time,
                    timezone=user.timezone
                ),
                parse_mode="HTML"
            )
    await callback.answer()