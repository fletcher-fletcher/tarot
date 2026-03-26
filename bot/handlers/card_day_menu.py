import random
from aiogram import Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from bot.keyboards.card_day_menu import get_card_day_menu, get_card_day_time_menu
from bot.keyboards.settings import get_time_menu, get_timezone_menu
from bot.keyboards.after_spread import get_after_spread_buttons
from bot.core.deck import get_card_by_id, get_all_card_ids
from bot.core.card_texts import CARD_TEXTS
from bot.config import settings
from bot.db import get_session, get_user, update_settings, create_user
from bot.services.limits import check_and_update_limit
from bot.services.groq import generate_tarot_reading

router = Router()


class CardDaySettingsStates(StatesGroup):
    waiting_for_time = State()
    waiting_for_timezone = State()


async def _send_card_to_user(
    user_id: int,
    username: str,
    first_name: str,
    context: str
):
    """Send card of the day to user"""
    
    logger.info(f"=== START _send_card_to_user for user {user_id} ===")
    
    # Check limit and get user settings
    async with get_session() as session:
        try:
            # Ensure user exists
            user = await get_user(session, user_id)
            if not user:
                logger.info(f"User {user_id} not found, creating...")
                user = await create_user(
                    session,
                    telegram_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=None
                )
                await session.commit()
                logger.info(f"User {user_id} created successfully")
            
            # Check limit
            logger.info(f"Calling check_and_update_limit with type='card_day'")
            can, used, limit = await check_and_update_limit(
                session, user_id, "card_day"
            )
            logger.info(f"Result: can={can}, used={used}, limit={limit}")
            
            if not can:
                logger.info(f"Limit exceeded for user {user_id}")
                # We need to send message, but we don't have message object here
                # Return False and let caller handle sending message
                return False, used, limit, None, None
            
            show_reversed = user.show_reversed if user else settings.DEFAULT_SHOW_REVERSED
            show_images = user.show_images if user else settings.DEFAULT_SHOW_IMAGES
            
            return True, show_reversed, show_images, used, limit
            
        except Exception as e:
            logger.error(f"Error in limit check: {e}", exc_info=True)
            return False, None, None, None, None
    
    # Note: This part will not be reached because of the return above
    # The actual card drawing and sending happens in the callback function


async def _draw_and_send_card(
    user_id: int,
    username: str,
    first_name: str,
    context: str,
    show_reversed: bool,
    show_images: bool
):
    """Draw and send card to user"""
    
    # Draw card
    try:
        logger.info("Drawing card...")
        all_cards = get_all_card_ids()
        card_id = random.choice(all_cards)
        card = get_card_by_id(card_id)
        
        is_reversed = random.random() < 0.3 if show_reversed else False
        card.is_reversed = is_reversed
        
        logger.info(f"Card drawn: {card.name_ru}, reversed={is_reversed}")
        
        SPHERES = {
            "general": "общей",
            "love": "отношений",
            "career": "карьеры",
            "self": "саморазвития",
            "warning": "предостережения"
        }
        
        # Generate reading via Groq
        problem_text = f"Карта дня в сфере {SPHERES.get(context, 'общей')}"
        
        try:
            reading = await generate_tarot_reading(
                scenario_name="Карта дня",
                problem_text=problem_text,
                cards=[card],
                spread_type="one_card",
                position_names=["Совет"]
            )
            logger.info("Reading generated successfully")
        except Exception as e:
            logger.error(f"Groq error in card_day: {e}")
            card_data = CARD_TEXTS.get(card.card_id, {})
            general_variants = card_data.get("general", [])
            reading = random.choice(general_variants) if general_variants else card.short_upright
        
        # Format text
        status = " (перевёрнутая)" if is_reversed else ""
        text = f"🎴 <b>КАРТА ДНЯ</b>\n\n"
        text += f"🃏 <b>{card.name_ru}</b>{status}\n\n"
        text += f"{reading}"
        
        # We need to send via bot, but we don't have the message object
        # Return the card data and let caller send it
        return {
            "success": True,
            "text": text,
            "image_path": settings.CARDS_DIR / f"{card.card_id}.jpg" if show_images else None,
            "card": card
        }
        
    except Exception as e:
        logger.error(f"Error in card drawing: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@router.message(Command("card"))
@router.message(lambda msg: msg.text == "🎴 КАРТА ДНЯ")
async def card_day_menu(message: Message):
    """Show card day menu"""
    await message.answer(
        "🎴 <b>КАРТА ДНЯ</b>\n\n"
        "Получите совет от карт на сегодня\n"
        "или настройте время для автоматической отправки.",
        reply_markup=get_card_day_menu(),
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data == "card_day:get")
async def get_card_day(callback: CallbackQuery):
    """Get card of the day"""
    # Use real user from callback, not from message
    real_user = callback.from_user
    user_id = real_user.id
    username = real_user.username
    first_name = real_user.first_name
    
    logger.info(f"Get card day for user: {user_id} (@{username})")
    
    # Check limit first
    async with get_session() as session:
        # Ensure user exists
        user = await get_user(session, user_id)
        if not user:
            logger.info(f"User {user_id} not found, creating...")
            user = await create_user(
                session,
                telegram_id=user_id,
                username=username,
                first_name=first_name,
                last_name=None
            )
            await session.commit()
            logger.info(f"User {user_id} created successfully")
        
        # Check limit
        can, used, limit = await check_and_update_limit(
            session, user_id, "card_day"
        )
        
        if not can:
            await callback.message.answer(
                f"⚠️ <b>Лимит карты дня исчерпан!</b>\n\n"
                f"Вы уже получили карту дня сегодня ({used}/{limit}).\n"
                f"Загляните завтра — будет новая карта! ✨",
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        show_reversed = user.show_reversed if user else settings.DEFAULT_SHOW_REVERSED
        show_images = user.show_images if user else settings.DEFAULT_SHOW_IMAGES
    
    # Send initial message
    await callback.message.answer(
        "🃏 <b>Ваша карта дня...</b>\n\n"
        "✨ Раскладываю карты...",
        parse_mode="HTML"
    )
    
    # Draw card
    try:
        all_cards = get_all_card_ids()
        card_id = random.choice(all_cards)
        card = get_card_by_id(card_id)
        
        is_reversed = random.random() < 0.3 if show_reversed else False
        card.is_reversed = is_reversed
        
        SPHERES = {
            "general": "общей",
            "love": "отношений",
            "career": "карьеры",
            "self": "саморазвития",
            "warning": "предостережения"
        }
        
        # Generate reading via Groq
        problem_text = f"Карта дня в сфере {SPHERES.get('general', 'общей')}"
        
        try:
            reading = await generate_tarot_reading(
                scenario_name="Карта дня",
                problem_text=problem_text,
                cards=[card],
                spread_type="one_card",
                position_names=["Совет"]
            )
        except Exception as e:
            logger.error(f"Groq error in card_day: {e}")
            card_data = CARD_TEXTS.get(card.card_id, {})
            general_variants = card_data.get("general", [])
            reading = random.choice(general_variants) if general_variants else card.short_upright
        
        # Format text
        status = " (перевёрнутая)" if is_reversed else ""
        text = f"🎴 <b>КАРТА ДНЯ</b>\n\n"
        text += f"🃏 <b>{card.name_ru}</b>{status}\n\n"
        text += f"{reading}"
        
        # Send with image if enabled
        if show_images:
            image_path = settings.CARDS_DIR / f"{card.card_id}.jpg"
            if image_path.exists():
                photo = FSInputFile(str(image_path))
                await callback.message.answer_photo(
                    photo=photo,
                    caption=text[:1024],
                    parse_mode="HTML",
                    reply_markup=get_after_spread_buttons()
                )
            else:
                await callback.message.answer(
                    text,
                    parse_mode="HTML",
                    reply_markup=get_after_spread_buttons()
                )
        else:
            await callback.message.answer(
                text,
                parse_mode="HTML",
                reply_markup=get_after_spread_buttons()
            )
        
        logger.info(f"Card sent successfully to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending card: {e}", exc_info=True)
        await callback.message.answer(
            "❌ Извините, произошла ошибка при получении карты. Попробуйте позже.",
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(lambda c: c.data == "card_day:settings")
async def card_day_settings(callback: CallbackQuery):
    """Show card day settings"""
    # Use real user from callback
    real_user = callback.from_user
    user_id = real_user.id
    
    async with get_session() as session:
        user = await get_user(session, user_id)
        
        tz_name = user.timezone if user else settings.DEFAULT_TIMEZONE
        for tz_code, tz_display in settings.TIMEZONES:
            if tz_code == tz_name:
                tz_name = tz_display
                break
        
        await callback.message.edit_text(
            f"⚙️ <b>Настройки карты дня</b>\n\n"
            f"⏰ Время: <b>{user.daily_card_time if user else settings.DEFAULT_DAILY_CARD_TIME}</b>\n"
            f"🌍 Часовой пояс: <b>{tz_name}</b>\n\n"
            f"Выберите, что хотите изменить:",
            reply_markup=get_card_day_time_menu(),
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(lambda c: c.data == "card_day:set_time")
async def set_card_day_time(callback: CallbackQuery):
    """Set card day time"""
    await callback.message.edit_text(
        "⏰ <b>Время карты дня</b>\n\n"
        "Выберите время для ежедневной рассылки:",
        reply_markup=get_time_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "card_day:set_timezone")
async def set_card_day_timezone(callback: CallbackQuery):
    """Set card day timezone"""
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
    real_user = callback.from_user
    user_id = real_user.id
    
    async with get_session() as session:
        await update_settings(session, user_id, daily_card_time=time_str)
        
        user = await get_user(session, user_id)
        
        tz_name = user.timezone if user else settings.DEFAULT_TIMEZONE
        for tz_code, tz_display in settings.TIMEZONES:
            if tz_code == tz_name:
                tz_name = tz_display
                break
        
        await callback.message.edit_text(
            f"⚙️ <b>Настройки карты дня</b>\n\n"
            f"⏰ Время: <b>{user.daily_card_time if user else settings.DEFAULT_DAILY_CARD_TIME}</b>\n"
            f"🌍 Часовой пояс: <b>{tz_name}</b>\n\n"
            f"Выберите, что хотите изменить:",
            reply_markup=get_card_day_time_menu(),
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("tz:"))
async def set_timezone(callback: CallbackQuery):
    """Set timezone"""
    tz_code = callback.data.split(":")[1]
    real_user = callback.from_user
    user_id = real_user.id
    
    async with get_session() as session:
        await update_settings(session, user_id, timezone=tz_code)
        
        user = await get_user(session, user_id)
        
        tz_name = user.timezone
        for tz_code2, tz_display in settings.TIMEZONES:
            if tz_code2 == tz_name:
                tz_name = tz_display
                break
        
        await callback.message.edit_text(
            f"⚙️ <b>Настройки карты дня</b>\n\n"
            f"⏰ Время: <b>{user.daily_card_time if user else settings.DEFAULT_DAILY_CARD_TIME}</b>\n"
            f"🌍 Часовой пояс: <b>{tz_name}</b>\n\n"
            f"Выберите, что хотите изменить:",
            reply_markup=get_card_day_time_menu(),
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(lambda c: c.data == "card_day:menu")
async def back_to_card_day_menu(callback: CallbackQuery):
    """Back to card day menu"""
    await callback.message.edit_text(
        "🎴 <b>КАРТА ДНЯ</b>\n\n"
        "Получите совет от карт на сегодня\n"
        "или настройте время для автоматической отправки.",
        reply_markup=get_card_day_menu(),
        parse_mode="HTML"
    )
    await callback.answer()