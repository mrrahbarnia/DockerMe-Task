from pydantic_settings import BaseSettings


class Outbox(BaseSettings):
    MAX_RETRIES: int
    BACKOFF_SEC: int
