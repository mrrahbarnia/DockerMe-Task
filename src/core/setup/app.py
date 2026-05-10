from fastapi import FastAPI

from .lifespan import lifespan

from src.core.config import ENVS
from src.modules.shared.constant import Environment


app: FastAPI = FastAPI(
    title="Dockerme.task",
    description="Technical test task for Dockerme interview",
    version="0.0.1",
    docs_url=None
    if ENVS.ENVIRONMENT == Environment.PRODUCTION
    else ENVS.FASTAPI.DOCS_URL,
    openapi_url=None
    if ENVS.ENVIRONMENT == Environment.PRODUCTION
    else ENVS.FASTAPI.OPENAPI_URL,
    redoc_url=None
    if ENVS.ENVIRONMENT == Environment.PRODUCTION
    else ENVS.FASTAPI.REDOC_URL,
    lifespan=lifespan,
)
