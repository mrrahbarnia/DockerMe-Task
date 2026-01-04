import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    # ============================== On startup
    logger.info("Application is running...")

    yield
    # ============================== On shutdown

    logger.info("Application is shutting down...")
