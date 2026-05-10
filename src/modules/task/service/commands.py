import logging
import asyncio

from . import exceptions as exc
from ..domain.models import Task as DomainTask
from ..domain.value_objects import TaskId

from src.modules.shared.infrastructure.unit_of_work import UOW
from src.modules.shared.constant import DBLock

logger = logging.getLogger(__name__)


async def create_task(uow: UOW, title: str) -> DomainTask:
    domain_task = DomainTask.create(title=title)
    async with uow:
        await uow.tasks.add(domain_task)
    return domain_task


async def delete_task(uow: UOW, task_id: TaskId) -> None:
    async with uow:
        task = await uow.tasks.delete(task_id)
        if not task:
            raise exc.EntityNotFound


async def run_task(uow: UOW, task_id: TaskId) -> DomainTask:
    async with uow:
        task = await uow.tasks.get_by_id(id=task_id, lock=DBLock(is_active=True))
        if not task:
            raise exc.EntityNotFound
        task.run()
        await uow.tasks.update(domain_task=task)
        return task


async def process_task(uow: UOW, task_id: TaskId):
    async with uow:
        task = await uow.tasks.get_by_id(id=task_id)
        if not task:
            logger.critical("Didn't find task with event task_id")
            raise exc.EntityNotFound
        await asyncio.to_thread(task.process)

    # Important: Why i open a new connection?
    # Because the process may take time(10 seconds) and i dont want the DB connection reserved for this time.
    async with uow:
        await uow.tasks.update(domain_task=task)
