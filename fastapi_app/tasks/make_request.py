import asyncio

import aiohttp
from fastapi import HTTPException, status

from fastapi_app.tasks.aiohttp_client import aiohttp_client


async def make_request(method, url, **kwargs):
    """
    Обертка над клиентом aiohttp для отправки HTTP-запросов.

    Параметры:
        method: str - метод HTTP-запроса
        url: str - URL, на который отправляется запрос
        **kwargs: дополнительные ключевые аргументы, которые передаются в клиент aiohttp

    Возвращает:
        response: dict - словарь с данными ответа
    """
    try:
        client = await aiohttp_client.get_client()
        async with client.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

    except aiohttp.ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=e.message)

    except aiohttp.ClientError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    except asyncio.TimeoutError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Timeout error")
