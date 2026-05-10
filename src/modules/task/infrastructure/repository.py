from typing import Set

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from .db_models import Task as DBTask
from ..domain.value_objects import TaskId
from ..domain.models import Task as DomainTask

from src.modules.shared.constant.db_lock import DBLock


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._seen: Set[DomainTask] = set()

    async def get_by_id(
        self,
        id: TaskId,
        lock: DBLock = DBLock(is_active=False),
    ) -> DomainTask | None:
        stmt = sa.select(DBTask).where(DBTask.id == id)

        if lock.is_active:
            await self.session.execute(
                sa.text(f"SET LOCAL lock_timeout = '{lock.timeout_second}s'")
            )
            stmt = stmt.with_for_update(skip_locked=lock.skip_locked)

        try:
            orm_task = await self.session.scalar(stmt)

            if orm_task is None:
                return None

            domain_task = DomainTask(
                id=orm_task.id,
                title=orm_task.title,
                status=orm_task.status,
                created_at=orm_task.created_at,
            )
            self._seen.add(domain_task)
            return domain_task

        except Exception:
            return None

    async def add(self, domain_task: DomainTask) -> None:
        stmt = sa.insert(DBTask).values(
            {
                DBTask.id: domain_task.id,
                DBTask.title: domain_task.title,
                DBTask.status: domain_task.status,
            }
        )
        self._seen.add(domain_task)
        await self.session.execute(stmt)

    async def delete(self, task_id: TaskId) -> TaskId | None:
        stmt = sa.delete(DBTask).where(DBTask.id == task_id).returning(DBTask.id)

        return await self.session.scalar(stmt)

    async def update(self, domain_task: DomainTask) -> None:
        stmt = (
            sa.update(DBTask)
            .values({DBTask.status: domain_task.status})
            .where(DBTask.id == domain_task.id)
        )

        self._seen.add(domain_task)

        await self.session.execute(stmt)


class TestRepository:
    # I can mock the repository for testing with an in-memory DB like sqlite
    ...
