from typing import Literal

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from . import exceptions as exc
from ..domain.models import Task as DomainTask
from ..domain.value_objects import TaskId
from ..infrastructure.db_models import Task as DBTask


async def get_task_list(
    session: AsyncSession, limit: int, offset: int, sort_mode: Literal["DESC", "ASC"]
) -> tuple[list[DomainTask], int | None]:
    stmt = (
        sa.select(DBTask)
        .limit(limit)
        .offset(offset)
        .order_by(
            DBTask.created_at.desc() if sort_mode == "DESC" else DBTask.created_at.asc()
        )
    )

    counter_stmt = sa.select(sa.func.count(DBTask.id))

    result = (await session.scalars(stmt)).all()
    count = await session.scalar(counter_stmt)
    return [
        DomainTask(
            id=task.id, title=task.title, status=task.status, created_at=task.created_at
        )
        for task in result
    ], count


async def get_task_detail(session: AsyncSession, task_id: TaskId) -> DomainTask:
    stmt = sa.select(DBTask).where(DBTask.id == task_id).limit(1)
    task = await session.scalar(stmt)
    if not task:
        raise exc.EntityNotFound
    return DomainTask(
        id=task.id, title=task.title, status=task.status, created_at=task.created_at
    )
