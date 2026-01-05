import pytest
import pytest_asyncio

from testcontainers.core.waiting_utils import wait_for_logs  # type: ignore
from testcontainers.postgres import PostgresContainer  # type: ignore
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from src.manager.common.db_metadata import BaseModel
from src.manager.dependencies.container import container
from src.modules.task.service.unit_of_work import (
    SqlAlchemyUnitOfWork as TaskSqlalchemyUnitOfWork,
)


pg_container = PostgresContainer(
    "postgres:17.4", username="test", password="test", dbname="test"
)


@pytest.fixture(scope="session")
def postgres_container():
    pg_container.start()
    wait_for_logs(
        pg_container, "database system is ready to accept connections", timeout=30
    )
    try:
        yield pg_container
    finally:
        pg_container.stop()


@pytest_asyncio.fixture(scope="function")
async def async_engine(postgres_container: PostgresContainer):
    port = postgres_container.get_exposed_port(pg_container.port)
    async_db_url = f"postgresql+asyncpg://test:test@localhost:{port}/test"

    engine = create_async_engine(async_db_url)

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session_maker(
    async_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(async_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def override_get_session(
    async_engine: AsyncEngine, async_session_maker: async_sessionmaker[AsyncSession]
) -> None:
    container.register(AsyncEngine, instance=async_engine)
    container.register(async_sessionmaker[AsyncSession], instance=async_session_maker)


@pytest_asyncio.fixture(scope="function")
async def uow(
    override_get_session, async_session_maker: async_sessionmaker[AsyncSession]
) -> TaskSqlalchemyUnitOfWork:
    return TaskSqlalchemyUnitOfWork(session_maker=async_session_maker)
