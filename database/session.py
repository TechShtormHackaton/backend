from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from core.global_config import settings

engine = create_async_engine(settings.database_uri)

async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """
    Генератор сессии
    :return: Возвращает асинхронную сессию
    """
    async with async_session_maker() as session:
        yield session
