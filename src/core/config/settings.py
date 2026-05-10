from pydantic_settings import BaseSettings, SettingsConfigDict

from . import schemas
from src.modules.shared.constant import Environment


class _ENVS(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
    )
    ENVIRONMENT: Environment
    POSTGRESQL: schemas.PostgreSQL
    FASTAPI: schemas.FastAPI
    OUTBOX: schemas.Outbox


ENVS = _ENVS()  # type: ignore
