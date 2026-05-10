from typing import AsyncGenerator, Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .infrastructure.db_metadata import SESSION_MAKER


async def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return SESSION_MAKER


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with SESSION_MAKER.begin() as session:
        yield session
