import logging
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from logging.config import dictConfig

from fastapi import FastAPI
from sqlalchemy import text

from .logger import LogConfig

from src.modules.shared.infrastructure.db_metadata import ASYNC_ENGINE
from src.modules.outbox.bootstrap import bootstrap


logger = logging.getLogger(__name__)

MAX_RETRIES = 5
RETRY_DELAY = 5


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    # ============================== On startup
    retry_number = 0
    is_postgres_ready = False

    logger.info("Logger is running...")
    dictConfig(LogConfig().model_dump())

    while not (is_postgres_ready):
        if retry_number >= MAX_RETRIES:
            raise RuntimeError(
                f"Infrastructure not ready after {MAX_RETRIES} attempts "
                f"(postgresql={is_postgres_ready})"
            )
        retry_number += 1
        logger.info(f"Startup check attempt {retry_number}/{MAX_RETRIES}")

        # ================ PostgreSQL check
        if not is_postgres_ready:
            try:
                async with ASYNC_ENGINE.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                logger.info("PostgreSQL is up and running.")
                is_postgres_ready = True
            except Exception as ex:
                logger.warning(f"PostgreSQL not ready: {ex}")

        # ================= Retry
        if not (is_postgres_ready):
            logger.info(f"Retrying in {RETRY_DELAY} seconds...")
            await asyncio.sleep(RETRY_DELAY)

    logger.info("Bootstrapping application requirements...")
    bootstrap()

    logger.info("Application is running...")

    yield
    # ============================== On shutdown

    logger.info("Application is shutting down...")
