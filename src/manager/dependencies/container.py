# This is a shared dependency injector for all modules
import punq  # type: ignore
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)

from src.manager.common.db_metadata import ASYNC_ENGINE, SESSION_MAKER


container = punq.Container()

container.register(AsyncEngine, instance=ASYNC_ENGINE)
container.register(async_sessionmaker[AsyncSession], instance=SESSION_MAKER)
