from typing import Optional
from urllib.parse import urlencode, urljoin

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from config import settings
from fastapi_app.auth.schema import UserDBSchema
from fastapi_app.auth.validation import get_current_auth_user
from fastapi_app.tasks.make_request import make_request
from fastapi_app.tasks.schema import (
    ListTasksResponseSchema,
    TaskFullSchema,
    TaskResponseSchema,
    TaskSchema,
    TaskUpdateSchema,
)

http_bearer = HTTPBearer(auto_error=False)
tasks_router = APIRouter(tags=["tasks"], dependencies=[Depends(http_bearer)])

base_url = f"http://{settings.aiohttp.host}:{settings.aiohttp.port}/tasks"


@tasks_router.get(
    "/",
    summary="Получение списка всех задач с возможностью фильтрации по статусу.",
    response_model=ListTasksResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_task_endpoint(
    task_status: Optional[str] = None,
    user: UserDBSchema = Depends(get_current_auth_user),
):
    """
    Получение списка задач

    Параметры:
        status: str - Сортировка по статусу задачи (по умолчанию None)

    Возвращает:
        message: str - Сообщение об успешном получении списка задач
        tasks: List[TaskFullSchema] - Список задач
    """
    if task_status:
        params = urlencode({"status": task_status})
        url = urljoin(base_url, "?" + params)
    else:
        url = base_url
    tasks = await make_request("GET", url)
    return {
        "message": "Список задач",
        "tasks": [TaskFullSchema(**task) for task in tasks["tasks"]],
    }


@tasks_router.post(
    "/",
    summary="Создание задачи",
    response_model=TaskResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task: TaskSchema,
    user: UserDBSchema = Depends(get_current_auth_user),
):
    """
    Создание задачи

    Параметры:
        title: str - название задачи
        description: str - описание задачи
        status: str - статус задачи (по умолчанию "Добавлена")

    Возвращает:
        message: str - сообщение об успешном создании, с информацией о созданной задаче
    """
    if not task.status:
        task.status = "Добавлена"
    task_dict = task.model_dump()
    task_dict["user_id"] = user.id
    created_task = await make_request("POST", base_url, json=task_dict)

    return {"message": "Задача создана", "task": TaskFullSchema(**created_task)}


@tasks_router.put(
    "/{task_id}/",
    summary="Oбновление задачи",
    response_model=TaskResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def update_task_endpoint(
    task_id: int,
    task_update: TaskUpdateSchema,
    user: UserDBSchema = Depends(get_current_auth_user),
):
    """
    Обновление задачи

    Параметры:
        id: int - id задачи
        title: str - название задачи
        description: str - описание задачи
        status: str - статус задачи

    Возвращает:
        message: str - сообщение об успешном обновлении, с информацией о обновленной задаче

    Ошибки:
        404 - задача не найдена
    """
    task_update_dict = task_update.model_dump()
    task_update_dict["id"] = task_id
    task = await make_request("PUT", base_url, json=task_update_dict)
    if task:
        return {"message": "Задача обновлена", "task": TaskFullSchema(**task)}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Задача с id {task_id} не найдена",
    )


@tasks_router.delete(
    "/{task_id}/",
    summary="Удаление задачи",
    response_model=TaskResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def delete_task_endpoint(
    task_id: int,
    user: UserDBSchema = Depends(get_current_auth_user),
):
    """
    Удаление задачи по id

    Параметры:
        id: int - id задачи

    Возвращает:
        message: str - сообщение об успешном удалении с id задачи

    Ошибки:
        404 - задача не найдена
    """
    url = f"{base_url}/{task_id}"
    deleted_task = await make_request("DELETE", url)
    if deleted_task:
        return {"message": "Задача удалена", "task": deleted_task}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Задача с id {task_id} не найдена",
    )
