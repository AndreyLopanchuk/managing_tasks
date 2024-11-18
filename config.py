from os import getenv
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AiohttpSettings(BaseSettings):
    host: str = "aiohttp"
    port: int = 8080


class PostgresSettings(BaseSettings):
    host: str = "postgres"
    port: int = 5432
    database: str = getenv("POSTGRES_DB", "task")
    user: str = getenv("POSTGRES_USER", "admin")
    password: str = getenv("POSTGRES_PASSWORD", "admin")


class RedisSettings(BaseSettings):
    host: str = "redis"
    port: int = 6379


class FastAPISettings(BaseSettings):
    title: str = "FastAPI App"
    description: str = "Managing the task list"
    version: str = "1.0.1"


class AuthJWT(BaseSettings):
    private_key_path: Path = Path("fastapi_app", "certs", "private.pem").resolve()
    public_key_path: Path = Path("fastapi_app", "certs", "public.pem").resolve()
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)
    aiohttp: AiohttpSettings = AiohttpSettings()
    postgres: PostgresSettings = PostgresSettings()
    fastapi: FastAPISettings = FastAPISettings()
    redis: RedisSettings = RedisSettings()
    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()
