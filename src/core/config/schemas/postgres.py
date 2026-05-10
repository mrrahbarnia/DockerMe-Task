from pydantic_settings import BaseSettings


class PostgreSQL(BaseSettings):
    HOST: str
    PORT: str
    DATABASE: str
    USERNAME: str
    PASSWORD: str

    @property
    def get_url(self):
        return f"postgresql+asyncpg://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"
