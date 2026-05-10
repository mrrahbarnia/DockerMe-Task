from ..infrastructure.repository import TaskRepository

from src.modules.shared.infrastructure.unit_of_work import UOW


async def get_uow() -> UOW:
    return UOW(task_repo_class=TaskRepository)
