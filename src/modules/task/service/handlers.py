from src.manager.dependencies.container import container
from src.events.service.messagebus import handler_register
from ..domain.events import TaskRan


@handler_register(TaskRan)
async def send_book_returned_notification(
    dict,
) -> None:
    event = TaskRan(**dict)
    print(event)
