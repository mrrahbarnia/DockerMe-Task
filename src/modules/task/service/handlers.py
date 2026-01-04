from src.events.service.messagebus import handler_register
from ..domain.events import TaskRan
from .commands import process_task
from .unit_of_work import SqlAlchemyUnitOfWork


@handler_register(TaskRan)
async def process_task_handler(
    dict,
) -> None:
    event = TaskRan(**dict)
    sqlachemy_uow = SqlAlchemyUnitOfWork()
    await process_task(uow=sqlachemy_uow, task_id=event.id)
