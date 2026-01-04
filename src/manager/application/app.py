from fastapi import FastAPI

from src.manager.config import ENVS
from src.manager.common.constants import Environment
from .lifespan import lifespan


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
