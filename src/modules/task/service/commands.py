import logging
import asyncio
from uuid import uuid4

from . import exceptions as exc
from .unit_of_work import IUnitOfWork
from ..domain.models import Task as DomainTask
from ..domain.types import TaskId

logger = logging.getLogger(__name__)


async def create_task(uow: IUnitOfWork, title: str) -> DomainTask:
    domain_task = DomainTask.create(id=TaskId(uuid4()), title=title)
    async with uow:
        await uow.tasks.add(domain_task)
    return domain_task


async def delete_task(uow: IUnitOfWork, task_id: TaskId) -> None:
    async with uow:
        task = await uow.tasks.delete(task_id)
        if not task:
            raise exc.EntityNotFound


async def run_task(uow: IUnitOfWork, task_id: TaskId) -> DomainTask:
    async with uow:
        task = await uow.tasks.get_by_id(id=task_id, lock=True)
        if not task:
            raise exc.EntityNotFound
        task.run()
        await uow.tasks.update(domain_task=task)
        return task


async def process_task(uow: IUnitOfWork, task_id: TaskId):
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
