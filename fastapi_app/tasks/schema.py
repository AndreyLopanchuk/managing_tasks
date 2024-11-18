from typing import Optional

from pydantic import BaseModel, Field


class TaskSchema(BaseModel):
    title: str
    description: str
    status: Optional[str] = None


class TaskFullSchema(TaskSchema):
    id: int
    user_id: Optional[int]


class TaskResponseSchema(BaseModel):
    message: str
    task: TaskFullSchema


class ListTasksResponseSchema(BaseModel):
    message: str
    tasks: Optional[list[TaskFullSchema]] = Field(default_factory=list)


class TaskIdResponseSchema(BaseModel):
    message: str
    task_id: int


class TaskUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
