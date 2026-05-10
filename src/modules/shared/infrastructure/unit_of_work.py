from typing import Self
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .db_metadata import SESSION_MAKER

from src.modules.outbox.infrastructure.repository import OutboxRepository
from src.modules.task.service.interfaces import ITaskRepository


def serialize(value):
    if isinstance(value, UUID):
        return str(value)

    # asyncpg UUID fallback
    if value.__class__.__name__ == "UUID":
        return str(value)

    return value


def safe_to_dict(data: dict) -> dict:
    return {k: serialize(v) for k, v in data.items()}


class UOW:
    def __init__(
        self,
        task_repo_class: type[ITaskRepository],
        session_maker: async_sessionmaker[AsyncSession] = SESSION_MAKER,
        outbox_repo_class: type[OutboxRepository] = OutboxRepository,
    ) -> None:
        self.session_maker = session_maker
        self.outbox_repo_class = outbox_repo_class
        self.task_repo_class = task_repo_class

    async def __aenter__(self) -> Self:
        session = self.session_maker()
        self.outbox = self.outbox_repo_class(session)
        self.tasks = self.task_repo_class(session)

        self.session = session
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback,
    ) -> None:
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.collect_new_events()
                await self.commit()
        finally:
            await self.session.close()

    async def rollback(self):
        return await self.session.rollback()

    async def commit(self):
        return await self.session.commit()

    async def collect_new_events(self):
        events = []
        if self.tasks._seen:
            for task in self.tasks._seen:
                while task.events:
                    events.append(task.events.pop(0))

        for event in events:
            await self.outbox.add(
                event_type=event.__class__.__name__,
                payload=safe_to_dict(event.to_dict()),
            )
