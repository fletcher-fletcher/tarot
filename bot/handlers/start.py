from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.main import get_main_keyboard
from bot.db import get_session, get_user, create_user

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    
    # Save user to database
    async with get_session() as session:
        user = await get_user(session, message.from_user.id)
        if not user:
            await create_user(
                session,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
    
    await message.answer(
        "✨ <b>Добро пожаловать в Tarot Bot!</b> ✨\n\n"
        "Я — ваш личный таролог. Выбирайте категорию и получайте совет от карт.\n\n"
        "🃏 <b>Колода:</b> Райдер — Уэйт (классика)\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(lambda msg: msg.text == "🏠 ГЛАВНОЕ МЕНЮ")
@router.message(lambda msg: msg.text == "🔙 НАЗАД")
async def back_to_main(message: Message):
    """Return to main menu from message"""
    await message.answer(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data == "menu:main")
async def back_to_main_callback(callback: CallbackQuery):
    """Return to main menu from callback"""
    await callback.message.delete()
    await callback.message.answer(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
    