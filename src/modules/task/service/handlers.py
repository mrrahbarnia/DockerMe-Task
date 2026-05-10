from src.modules.outbox.service.messagebus import handler_register
from ..domain.events import TaskRan
from .commands import process_task

from src.modules.shared.constant import EventContext


@handler_register(TaskRan)
async def process_task_handler(event: TaskRan, ctx: EventContext) -> None:
    await process_task(uow=ctx.uow, task_id=event.task_id)
