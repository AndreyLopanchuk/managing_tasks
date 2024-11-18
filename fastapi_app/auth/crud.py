from typing import Optional

import asyncpg

from fastapi_app.auth.schema import UserDBSchema


async def get_user(conn: asyncpg.Connection, username: str) -> Optional[UserDBSchema]:
    query = """
        SELECT * FROM users
        WHERE username = $1
    """
    record = await conn.fetchrow(query, username)
    if record:
        return UserDBSchema(**dict(record))

    return None


async def create_user(conn: asyncpg.Connection, username: str, password_hash: bytes) -> str:
    query = """
        INSERT INTO users (username, password_hash)
        VALUES ($1, $2)
        ON CONFLICT (username) DO NOTHING
        RETURNING username;
    """
    return await conn.fetchval(query, username, password_hash)
