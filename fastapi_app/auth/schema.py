from pydantic import BaseModel, ConfigDict


class UserDBSchema(BaseModel):
    id: int
    username: str
    password_hash: bytes

    model_config = ConfigDict(strict=True)


class UserSchema(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class RegisterResponseSchema(BaseModel):
    message: str
    username: str


class TokensSchema(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
