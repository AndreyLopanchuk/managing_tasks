import datetime
from typing import Annotated

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPBasic, HTTPBearer, OAuth2PasswordRequestForm
from redis import Redis

from config import settings
from fastapi_app.auth.crud import create_user, get_user
from fastapi_app.auth.schema import RegisterResponseSchema, TokensSchema, UserDBSchema, UserSchema
from fastapi_app.auth.security import create_access_token, create_refresh_token, hash_password, validate_password
from fastapi_app.auth.validation import get_current_auth_user_for_refresh
from fastapi_app.database.pg_accessor import db
from fastapi_app.database.redis_accessor import redis_client

security = HTTPBasic()
http_bearer = HTTPBearer(auto_error=False)
auth_router = APIRouter(tags=["auth"], dependencies=[Depends(http_bearer)])


@auth_router.post(
    "/register/",
    summary="Регистрация нового пользователя",
    status_code=201,
    response_model=RegisterResponseSchema,
)
async def register_user_endpoint(
    conn: Annotated[asyncpg.Connection, Depends(db.get_conn)],
    user: UserSchema,
):
    password_hash = await hash_password(user.password)
    username = await create_user(
        conn=conn,
        username=user.username,
        password_hash=password_hash,
    )
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует",
        )
    return {"message": "Пользователь зарегистрирован", "username": username}


@auth_router.post(
    "/login/",
    summary="Выдача токенов по логину и паролю",
    status_code=200,
    response_model=TokensSchema,
)
async def login(
    response: Response,
    conn: Annotated[asyncpg.Connection, Depends(db.get_conn)],
    form_data: OAuth2PasswordRequestForm = Depends(),
    redis: Redis = Depends(redis_client),
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неправильное имя пользователя или пароль",
    )
    if not (db_user := await get_user(conn=conn, username=form_data.username)):
        raise unauthed_exc

    if not await validate_password(password=form_data.password, hashed_password=db_user.password_hash):
        raise unauthed_exc
    access_token = await create_access_token(db_user)
    refresh_token = await create_refresh_token(db_user)
    expire_delta = settings.auth_jwt.refresh_token_expire_days * 24 * 60 * 60
    await redis.set(str(db_user.id), refresh_token, ex=expire_delta)
    expires = datetime.datetime.now() + datetime.timedelta(days=30)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="strict",
        expires=expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT"),
    )

    return {"access_token": access_token}


@auth_router.post(
    "/refresh/",
    summary="Продление access токена по refresh",
    status_code=200,
    response_model=TokensSchema,
    response_model_exclude_none=True,
)
async def refresh(
    response: Response,
    user: UserDBSchema = Depends(get_current_auth_user_for_refresh),
):
    access_token = await create_access_token(user)
    return {"access_token": access_token}
