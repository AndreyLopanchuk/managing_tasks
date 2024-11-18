import datetime

import bcrypt
import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError

from config import settings
from fastapi_app.auth.schema import UserDBSchema


async def hash_password(password: str) -> bytes:
    """Хэширует пароль с помощью bcrypt."""
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


async def validate_password(password: str, hashed_password: bytes) -> bool:
    """Проверяет, совпадает ли обычный пароль с хэшированным."""
    return bcrypt.checkpw(password.encode(), hashed_password)


async def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: datetime.timedelta | None = None,
) -> str:
    """Кодирует токен приватным ключом."""
    to_encode = payload.copy()
    now = datetime.datetime.now()
    if expire_timedelta:
        expire = datetime.datetime.now() + expire_timedelta
    else:
        expire = now + datetime.timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, private_key, algorithm=algorithm)


async def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    """Декодирует токен публичным ключом."""
    try:
        decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )

    return decoded


async def create_token(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: datetime.timedelta | None = None,
) -> str:
    """Cоздает токен."""
    jwt_payload = {"type": token_type}
    jwt_payload.update(token_data)
    return await encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


async def create_access_token(user: UserDBSchema) -> str:
    """Создает токен доступа."""
    jwt_payload = {"sub": user.id, "username": user.username}
    return await create_token(
        token_type="access",
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


async def create_refresh_token(user: UserDBSchema) -> str:
    """Создает токен обновления."""
    jwt_payload = {"sub": user.id, "username": user.username}
    return await create_token(
        token_type="refresh",
        token_data=jwt_payload,
        expire_timedelta=datetime.timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )
