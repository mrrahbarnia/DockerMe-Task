from typing import Protocol

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from .orm import Task as ORMTask
from ..domain.types import TaskId
from ..domain.models import Task as DomainTask


class IRepository(Protocol):
    def __init__(self, session: AsyncSession) -> None: ...
    async def get_by_id(self, id: TaskId, lock: bool = False) -> DomainTask | None: ...
    async def add(self, domain_task: DomainTask) -> None: ...
    async def delete(self, task_id: TaskId) -> TaskId | None: ...


class SqlAlchemyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        # self._seen: Set[DomainBook] = set()

    async def get_by_id(self, id: TaskId, lock: bool = False) -> DomainTask | None:
        stmt = sa.select(ORMTask).where(ORMTask.id == id)

        if lock:
            # We can get lock_timeout as a parameter too,but for simplicity the hardcoded value is ok.
            await self.session.execute(sa.text("SET LOCAL lock_timeout = '2s'"))
            stmt = stmt.with_for_update()

        try:
            orm_task = await self.session.scalar(stmt)
        except Exception:
            return None

        if orm_task is None:
            return None

        domain_book = DomainTask(
            id=orm_task.id,
            title=orm_task.title,
            status=orm_task.status,
        )
        # self._seen.add(domain_book)

        return domain_book

    async def add(self, domain_task: DomainTask) -> None:
        stmt = sa.insert(ORMTask).values(
            {
                ORMTask.id: domain_task.id,
                ORMTask.title: domain_task.title,
                ORMTask.status: domain_task.status,
            }
        )
        await self.session.execute(stmt)

    async def delete(self, task_id: TaskId) -> TaskId | None:
        stmt = sa.delete(ORMTask).where(ORMTask.id == task_id).returning(ORMTask.id)

        return await self.session.scalar(stmt)


class TestRepository:
    # I can mock the repository for testing with an in-memory DB like sqlite
    ...
