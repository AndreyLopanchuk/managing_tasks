import asyncpg

from config import settings

DATABASE_URL = "postgresql://{user}:{password}@{host}:{port}/{db}".format(
    user=settings.postgres.user,
    password=settings.postgres.password,
    host=settings.postgres.host,
    port=settings.postgres.port,
    db=settings.postgres.database,
)


class PostgresAccessor:
    """Класс для работы с базой данных PostgreSQL + asyncpg."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None

    async def get_conn(self):
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            yield conn

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.database_url)

    async def disconnect(self):
        await self.pool.close()
        self.pool = None


db = PostgresAccessor(database_url=DATABASE_URL)


async def create_tables():
    """Создает таблицы users и tasks."""
    async for conn in db.get_conn():
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash BYTEA NOT NULL
            )
        """
        )

        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                status VARCHAR(255) NOT NULL DEFAULT 'new',
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
            )
        """
        )
