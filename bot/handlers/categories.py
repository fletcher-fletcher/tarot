"""Handlers for three-level category menu"""

import random
import os
import re
from aiogram import Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.keyboards.categories import (
    get_main_category_menu,
    get_subcategory_menu,
    get_problem_menu,
)
from bot.keyboards.after_spread import get_after_spread_buttons
from bot.core.deck import get_random_card
from bot.core.spread_renderer import spread_renderer
from bot.scenarios import CATEGORIES, SUBCATEGORIES, PROBLEMS, get_problem_by_code
from bot.config import settings
from bot.db import get_session, get_user
from bot.services.limits import check_and_update_limit
from bot.services.groq import generate_tarot_reading
from bot.utils.helpers import smart_truncate

router = Router()


@router.message(Command("spreads"))
@router.message(lambda msg: msg.text == "🔮 РАСКЛАДЫ")
async def show_categories_menu(message: Message):
    """Show categories menu"""
    await message.answer(
        "🔮 <b>Выберите категорию:</b>",
        reply_markup=get_main_category_menu(),
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    """Back to main categories"""
    await callback.message.delete()
    await callback.message.answer(
        "🔮 <b>Выберите категорию:</b>",
        reply_markup=get_main_category_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("back_to_sub:"))
async def back_to_subcategory(callback: CallbackQuery):
    """Back to subcategories"""
    category_code = callback.data.split(":")[1]
    
    await callback.message.edit_text(
        f"📌 <b>{CATEGORIES.get(category_code, category_code)}</b>\n\n"
        f"Выберите, что вас интересует:",
        reply_markup=get_subcategory_menu(category_code),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("cat:"))
async def handle_category(callback: CallbackQuery):
    """Level 1: Category selected"""
    category_code = callback.data.split(":")[1]
    
    await callback.message.edit_text(
        f"📌 <b>{CATEGORIES.get(category_code, category_code)}</b>\n\n"
        f"Выберите, что вас интересует:",
        reply_markup=get_subcategory_menu(category_code),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("sub:"))
async def handle_subcategory(callback: CallbackQuery):
    """Level 2: Subcategory selected"""
    _, category_code, subcategory_code = callback.data.split(":")
    
    subcategory_name = SUBCATEGORIES.get(category_code, {}).get(subcategory_code, subcategory_code)
    
    await callback.message.edit_text(
        f"📌 <b>{CATEGORIES.get(category_code)} → {subcategory_name}</b>\n\n"
        f"Выберите ситуацию, которая откликается:",
        reply_markup=get_problem_menu(category_code, subcategory_code),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("prob:"))
async def handle_problem(callback: CallbackQuery):
    """Level 3: Problem selected - perform spread"""
    _, category_code, subcategory_code, problem_code = callback.data.split(":")
    
    # Get problem details
    problem = get_problem_by_code(category_code, subcategory_code, problem_code)
    if not problem:
        await callback.message.answer("❌ Ситуация не найдена")
        await callback.answer()
        return
    
    # Check limit
    async with get_session() as session:
        can, used, limit = await check_and_update_limit(
            session, callback.from_user.id, "spread"
        )
        
        if not can:
            await callback.message.answer(
                f"⚠️ <b>Лимит раскладов исчерпан!</b>\n\n"
                f"Вы уже использовали {used}/{limit} раскладов сегодня.\n"
                f"Лимиты обновятся завтра. ✨",
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        user = await get_user(session, callback.from_user.id)
        show_reversed = user.show_reversed if user else settings.DEFAULT_SHOW_REVERSED
        show_images = user.show_images if user else settings.DEFAULT_SHOW_IMAGES
    
    # Determine spread type
    spread_type = problem.get("spread", "three_cards")
    
    # Get positions from problem or use defaults
    positions = problem.get("positions", None)
    if not positions:
        if spread_type == "one_card":
            positions = ["Совет"]
        elif spread_type == "two_cards":
            positions = ["Корень проблемы", "Решение"]
        else:
            positions = ["Ситуация сейчас", "Препятствие", "Итог"]
    
    # Draw cards
    if spread_type == "one_card":
        cards = [get_random_card(reversed_allowed=show_reversed)]
    elif spread_type == "two_cards":
        cards = [get_random_card(reversed_allowed=show_reversed) for _ in range(2)]
    else:
        cards = [get_random_card(reversed_allowed=show_reversed) for _ in range(3)]
    
    # Generate reading via Groq
    try:
        reading = await generate_tarot_reading(
            scenario_name=problem["text"],
            problem_text=problem["text"],
            cards=cards,
            spread_type=spread_type,
            position_names=positions
        )
    except Exception as e:
        logger.error(f"Groq error: {e}")
        reading = "Извините, сейчас не могу дать толкование. Попробуйте позже."
    
    # Send response
    if show_images and spread_type != "one_card":
        try:
            cards_for_render = []
            for i, card in enumerate(cards):
                pos_name = positions[i] if i < len(positions) else f"Карта {i+1}"
                cards_for_render.append((card, {"name": pos_name}))
            
            image_path = await spread_renderer.create_spread_image(
                spread_name=problem["text"][:50],
                spread_id=f"{category_code}_{subcategory_code}",
                cards=cards_for_render,
                question=None,
                total_meaning=""
            )
            
            photo = FSInputFile(image_path)
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=photo,
                caption=None,
                reply_markup=None
            )
            
            await callback.message.answer(
                smart_truncate(reading, 4096),
                parse_mode="HTML",
                reply_markup=get_after_spread_buttons()
            )
            
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            logger.error(f"Image creation failed: {e}")
            await callback.message.delete()
            await callback.message.answer(
                smart_truncate(reading, 4096),
                parse_mode="HTML",
                reply_markup=get_after_spread_buttons()
            )
    else:
        await callback.message.delete()
        await callback.message.answer(
            smart_truncate(reading, 4096),
            parse_mode="HTML",
            reply_markup=get_after_spread_buttons()
        )
    
    await callback.answer()


@router.callback_query(lambda c: c.data == "new_spread")
async def new_spread(callback: CallbackQuery):
    """Start new spread"""
    await callback.message.delete()
    await callback.message.answer(
        "🔮 <b>Выберите категорию:</b>",
        reply_markup=get_main_category_menu(),
        parse_mode="HTML"
    )
    await callback.answer()