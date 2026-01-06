from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.task.service.unit_of_work import SqlAlchemyUnitOfWork
from src.modules.task.service import commands, queries


async def test_create_task_successfully(uow: SqlAlchemyUnitOfWork):
    t = await commands.create_task(uow=uow, title="Test Task")

    assert t.title == "Test Task"


async def test_get_task_detail_successfully(
    uow: SqlAlchemyUnitOfWork, async_session_maker: async_sessionmaker[AsyncSession]
):
    created_task = await commands.create_task(uow=uow, title="Test Task")
    async with async_session_maker.begin() as session:
        fetched_task = await queries.get_task_detail(
            session=session, task_id=created_task.id
        )

    assert created_task.id == fetched_task.id
    assert created_task.title == fetched_task.title
