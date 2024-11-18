from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from config import settings
from fastapi_app.auth.routes import auth_router
from fastapi_app.database.pg_accessor import create_tables, db
from fastapi_app.database.redis_accessor import close_async_redis_client, set_async_redis_client
from fastapi_app.tasks.aiohttp_client import aiohttp_client, create_aiohttp_client
from fastapi_app.tasks.routes import tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await set_async_redis_client()
    await create_aiohttp_client()
    yield
    await aiohttp_client.close()
    await db.disconnect()
    await close_async_redis_client()


main_app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    title=settings.fastapi.title,
    discription=settings.fastapi.description,
    version=settings.fastapi.version,
)

main_app.include_router(auth_router, prefix="/auth")
main_app.include_router(tasks_router, prefix="/tasks")
