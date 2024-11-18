from typing import Optional

import aiohttp
from aiohttp import ClientSession


class AiohttpClientSession:
    _instance: Optional["AiohttpClientSession"] = None
    _client: Optional[ClientSession] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._client = ClientSession(timeout=aiohttp.ClientTimeout(total=5))
        return cls._instance

    async def get_client(self) -> ClientSession:
        return self._client

    async def close(self):
        if self._client:
            await self._client.close()


aiohttp_client = AiohttpClientSession()


async def create_aiohttp_client() -> ClientSession:
    return await aiohttp_client.get_client()
