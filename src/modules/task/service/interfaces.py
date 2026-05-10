from typing import Protocol, Set

from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.value_objects import TaskId
from ..domain.models import Task as DomainTask

from src.modules.shared.constant import DBLock

# ==================================== Repository interface


class ITaskRepository(Protocol):
    _seen: Set[DomainTask] = set()

    def __init__(self, session: AsyncSession) -> None: ...
    async def get_by_id(
        self,
        id: TaskId,
        lock: DBLock = DBLock(is_active=False),
    ) -> DomainTask | None: ...
    async def add(self, domain_task: DomainTask) -> None: ...
    async def delete(self, task_id: TaskId) -> TaskId | None: ...
    async def update(self, domain_task: DomainTask) -> None: ...
