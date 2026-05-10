from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.types import UUID, DateTime
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)

from src.core.config import ENVS
from src.modules.task.domain.types import TaskId

ASYNC_ENGINE: AsyncEngine = create_async_engine(ENVS.POSTGRESQL.get_url)
SESSION_MAKER: async_sessionmaker[AsyncSession] = async_sessionmaker(
    ASYNC_ENGINE, expire_on_commit=False
)


class BaseModel(DeclarativeBase, MappedAsDataclass):
    type_annotation_map = {
        TaskId: UUID(as_uuid=True),
        datetime: DateTime(timezone=True),
    }
