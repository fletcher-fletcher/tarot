from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager

from bot.config import settings

# Создаем engine с разными настройками в зависимости от типа БД
if "sqlite" in settings.DATABASE_URL:
    # SQLite не поддерживает pool_size и max_overflow
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False}  # Для SQLite
    )
else:
    # PostgreSQL с пулом соединений
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_session():
    """Get database session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
