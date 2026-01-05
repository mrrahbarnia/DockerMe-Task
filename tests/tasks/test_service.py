from src.modules.task.service.unit_of_work import SqlAlchemyUnitOfWork
from src.modules.task.service import commands, queries


async def test_get_task_detail(uow: SqlAlchemyUnitOfWork):
    t = await commands.create_task(uow=uow, title="Test Task")

    assert t.title == "Test Task"
