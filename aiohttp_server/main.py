import asyncpg
from aiohttp import web

from aiohttp_server.database import DATABASE_URL
from aiohttp_server.routes import routes

app = web.Application()


async def init_db(app):
    app["pool"] = await asyncpg.create_pool(DATABASE_URL)


async def close_db(app):
    await app["pool"].close()


app.on_startup.append(init_db)
app.on_cleanup.append(close_db)

app.router.add_routes(routes)
