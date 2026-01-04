from uuid import uuid4

from . import exceptions as exc
from .unit_of_work import IUnitOfWork
from ..domain.models import Task as DomainTask
from ..domain.types import TaskId


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
