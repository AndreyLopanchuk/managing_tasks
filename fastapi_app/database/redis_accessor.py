from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis

from config import settings


class AsyncRedisClient:
    _client: Optional[Redis] = None

    @classmethod
    async def initialize(cls):
        if cls._client is None:
            cls._client = await aioredis.from_url(
                f"redis://{settings.redis.host}:{settings.redis.port}",
                max_connections=20,
                encoding="utf8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
        return cls._client

    @classmethod
    async def get_client(cls):
        return cls._client

    @classmethod
    async def close(cls):
        await cls._client.close()


async def redis_client() -> Redis:
    return await AsyncRedisClient.get_client()


async def set_async_redis_client() -> Redis:
    return await AsyncRedisClient.initialize()


async def close_async_redis_client():
    await AsyncRedisClient.close()
