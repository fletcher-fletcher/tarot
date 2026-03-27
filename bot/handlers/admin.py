"""Admin commands for bot management"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
import io
import csv
from datetime import datetime, timedelta

from bot.db import get_session
from bot.db.models import User, History
from sqlalchemy import select, func, and_

router = Router()

# ID администратора (ваш Telegram ID)
ADMIN_IDS = [5333876901]  # замените на ваш ID, если нужно


class BroadcastStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_image = State()


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS


@router.message(Command("stats"))
async def show_stats(message: Message):
    """Show bot statistics (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет прав для этой команды.")
        return
    
    await message.answer("📊 Собираю статистику...")
    
    async with get_session() as session:
        # Общее количество пользователей
        total_users = await session.scalar(select(func.count()).select_from(User))
        
        # Пользователи с уведомлениями
        notify_users = await session.scalar(
            select(func.count()).select_from(User)
            .where(User.notifications_enabled == True)
        )
        
        # Активные за сегодня
        today = datetime.utcnow().date()
        active_today = await session.scalar(
            select(func.count(func.distinct(History.user_id)))
            .select_from(History)
            .where(func.date(History.created_at) == today)
        )
        
        # Активные за неделю
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_week = await session.scalar(
            select(func.count(func.distinct(History.user_id)))
            .select_from(History)
            .where(History.created_at >= week_ago)
        )
        
        # Раскладов за сегодня
        spreads_today = await session.scalar(
            select(func.count()).select_from(History)
            .where(func.date(History.created_at) == today)
        )
        
        # Новые пользователи за неделю
        new_users_week = await session.scalar(
            select(func.count()).select_from(User)
            .where(User.created_at >= week_ago)
        )
        
        # Последние 10 пользователей
        recent = await session.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(10)
        )
        recent_users = recent.scalars().all()
        
        # Формируем сообщение
        stats = f"📊 <b>СТАТИСТИКА БОТА</b>\n\n"
        stats += f"👥 <b>Пользователи:</b>\n"
        stats += f"   ├ Всего: <code>{total_users}</code>\n"
        stats += f"   ├ С уведомлениями: <code>{notify_users}</code>\n"
        stats += f"   ├ Новые за неделю: <code>{new_users_week}</code>\n"
        stats += f"   └ Активные:\n"
        stats += f"       ├ сегодня: <code>{active_today or 0}</code>\n"
        stats += f"       └ за 7 дней: <code>{active_week or 0}</code>\n\n"
        
        stats += f"📖 <b>Расклады:</b>\n"
        stats += f"   └ сегодня: <code>{spreads_today}</code>\n\n"
        
        stats += f"🆕 <b>Последние пользователи:</b>\n"
        for u in recent_users:
            name = u.first_name or u.username or str(u.telegram_id)
            date = u.created_at.strftime('%d.%m %H:%M')
            stats += f"   • {name} — {date}\n"
        
        await message.answer(stats, parse_mode="HTML")


@router.message(Command("users"))
async def export_users(message: Message):
    """Export users list as CSV (admin only)"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer("📋 Экспортирую список пользователей...")
    
    async with get_session() as session:
        result = await session.execute(
            select(
                User.telegram_id,
                User.username,
                User.first_name,
                User.last_name,
                User.daily_card_time,
                User.timezone,
                User.notifications_enabled,
                User.created_at
            ).order_by(User.created_at.desc())
        )
        users = result.all()
        
        # Создаем CSV
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow([
            "telegram_id", "username", "first_name", "last_name",
            "daily_card_time", "timezone", "notifications", "created_at"
        ])
        
        for u in users:
            writer.writerow([
                u[0], u[1] or "", u[2] or "", u[3] or "",
                u[4], u[5], "да" if u[6] else "нет", u[7].strftime('%Y-%m-%d %H:%M')
            ])
        
        csv_bytes = output.getvalue().encode('utf-8-sig')
        await message.answer_document(
            document=io.BytesIO(csv_bytes),
            filename=f"users_{datetime.now().strftime('%Y%m%d')}.csv",
            caption=f"📋 Всего пользователей: {len(users)}"
        )


@router.message(Command("broadcast"))
async def broadcast_start(message: Message, state: FSMContext):
    """Start broadcast (admin only)"""
    if not is_admin(message.from_user.id):
        return
    
    # Проверяем, есть ли текст после команды
    text = message.text.replace("/broadcast", "").strip()
    
    if text:
        # Если текст есть в команде, отправляем сразу
        await send_broadcast(message, text, None)
    else:
        await message.answer(
            "📢 <b>РАССЫЛКА</b>\n\n"
            "Введите текст сообщения для рассылки.\n"
            "Если нужно добавить изображение, отправьте сначала текст, "
            "а затем на запрос пришлите фото.\n\n"
            "❌ Для отмены введите /cancel",
            parse_mode="HTML"
        )
        await state.set_state(BroadcastStates.waiting_for_text)


@router.message(BroadcastStates.waiting_for_text)
async def broadcast_get_text(message: Message, state: FSMContext):
    """Get broadcast text and ask for image"""
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    
    text = message.text
    if text == "/cancel":
        await state.clear()
        await message.answer("❌ Рассылка отменена.")
        return
    
    await state.update_data(text=text)
    
    await message.answer(
        "📷 Отправьте изображение (необязательно) или нажмите /skip чтобы пропустить.\n\n"
        "❌ /cancel - отмена",
        parse_mode="HTML"
    )
    await state.set_state(BroadcastStates.waiting_for_image)


@router.message(BroadcastStates.waiting_for_image, F.photo)
async def broadcast_get_image(message: Message, state: FSMContext):
    """Get broadcast image"""
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    
    photo = message.photo[-1]  # Самое большое изображение
    file_id = photo.file_id
    
    data = await state.get_data()
    text = data.get("text")
    
    await send_broadcast(message, text, file_id)
    await state.clear()


@router.message(BroadcastStates.waiting_for_image, F.text == "/skip")
async def broadcast_skip_image(message: Message, state: FSMContext):
    """Skip image and send broadcast"""
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    
    data = await state.get_data()
    text = data.get("text")
    
    await send_broadcast(message, text, None)
    await state.clear()


@router.message(BroadcastStates.waiting_for_image, F.text == "/cancel")
async def broadcast_cancel(message: Message, state: FSMContext):
    """Cancel broadcast"""
    await state.clear()
    await message.answer("❌ Рассылка отменена.")


async def send_broadcast(admin_message: Message, text: str, image_file_id: str = None):
    """Send broadcast to all users"""
    await admin_message.answer("📢 Начинаю рассылку...")
    
    async with get_session() as session:
        result = await session.execute(select(User.telegram_id))
        users = result.scalars().all()
    
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            if image_file_id:
                await admin_message.bot.send_photo(
                    chat_id=user_id,
                    photo=image_file_id,
                    caption=text,
                    parse_mode="HTML"
                )
            else:
                await admin_message.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode="HTML"
                )
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"Failed to send to {user_id}: {e}")
    
    await admin_message.answer(
        f"✅ Рассылка завершена!\n\n"
        f"📨 Отправлено: {success}\n"
        f"❌ Ошибок: {failed}\n"
        f"👥 Всего пользователей: {len(users)}"
    )


@router.message(Command("test_broadcast"))
async def test_broadcast(message: Message):
    """Send test broadcast to admin only (for testing)"""
    if not is_admin(message.from_user.id):
        return
    
    text = message.text.replace("/test_broadcast", "").strip()
    if not text:
        await message.answer("Использование: /test_broadcast текст сообщения")
        return
    
    await message.answer(f"📢 Тестовая рассылка (только вам):\n\n{text}")
