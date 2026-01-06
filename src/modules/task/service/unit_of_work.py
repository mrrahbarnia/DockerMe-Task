from typing import Protocol, Self
from dataclasses import asdict

import orjson
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from ..adapters.repository import (
    IRepository as TaskIRepository,
    SqlAlchemyRepository as TaskSqlAlchemyRepository,
)
from src.manager.dependencies.container import container
from src.events.adapters.repository import (
    IRepository as EventIRepository,
    SqlAlchemyRepository as EventSqlAlchemyRepository,
)


async_session_maker: async_sessionmaker[AsyncSession] = container.resolve(
    async_sessionmaker[AsyncSession]
)  # type: ignore


class IUnitOfWork(Protocol):
    tasks: TaskIRepository
    events: EventIRepository

    async def __aenter__(self) -> Self: ...
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback,
    ) -> None: ...


class SqlAlchemyUnitOfWork:
    tasks: TaskIRepository
    events: EventIRepository

    def __init__(
        self, session_maker: async_sessionmaker[AsyncSession] = async_session_maker
    ) -> None:
        self.session_maker = session_maker

    async def __aenter__(self) -> Self:
        session = self.session_maker()
        self.tasks = TaskSqlAlchemyRepository(session)
        self.events = EventSqlAlchemyRepository(session)
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
        for book in self.tasks._seen:
            while book.events:
                event = book.events.pop(0)

                payload_bytes = orjson.dumps(asdict(event))  # type: ignore
                payload_json = orjson.loads(payload_bytes)

                await self.events.add(
                    event_type=event.__class__.__name__, payload=payload_json
                )


class FakeUnitOfWork:
    # For testing
    ...
