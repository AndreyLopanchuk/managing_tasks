from datetime import datetime
from typing import Annotated, Optional

import asyncpg
from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from redis import Redis

from fastapi_app.auth.crud import get_user
from fastapi_app.auth.schema import UserDBSchema
from fastapi_app.auth.security import decode_jwt
from fastapi_app.database.pg_accessor import db
from fastapi_app.database.redis_accessor import redis_client

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_token_pyload(
    token: str = Depends(oauth_scheme),
) -> dict:
    """Получение bearer токена из заголовка и возврат payload"""
    return await decode_jwt(token=token)


async def get_current_auth_user(
    conn: Annotated[asyncpg.Connection, Depends(db.get_conn)],
    payload: dict = Depends(get_current_token_pyload),
) -> UserDBSchema:
    """Получение пользователя по payload"""
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{token_type!r} Неправильный тип токена",
        )
    username: Optional[str] = payload.get("username")
    if username:
        if user := await get_user(conn=conn, username=username):
            return user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")


async def get_current_auth_user_for_refresh(
    conn: Annotated[asyncpg.Connection, Depends(db.get_conn)],
    refresh_token: str = Cookie(None),
    redis: Redis = Depends(redis_client),
) -> UserDBSchema:
    """Получение пользователя по payload и проверка подлинности его refresh токена"""
    payload: dict = await decode_jwt(token=refresh_token)
    username: Optional[str] = payload.get("username")
    if username:
        if user := await get_user(conn=conn, username=username):
            original_refresh_token = await redis.get(str(user.id))
            original_pyload = await decode_jwt(token=original_refresh_token)
            exp_time = original_pyload.get("exp")
            if exp_time and datetime.fromtimestamp(exp_time) > datetime.now():
                if original_refresh_token == refresh_token:
                    return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный refresh токен",
    )
