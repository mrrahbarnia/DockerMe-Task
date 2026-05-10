from typing import Annotated
from datetime import datetime

from pydantic import BaseModel, Field, AfterValidator

from ...domain.value_objects import TaskId, TaskStatusEnum

from src.modules.shared.constant import PaginationSchema

StrippedStr = Annotated[str, AfterValidator(lambda x: x.strip())]


class CreateTaskRequest(BaseModel):
    title: Annotated[StrippedStr, Field(max_length=250)]


class CreateTaskResponse(CreateTaskRequest):
    id: TaskId


class DetailTaskResponse(BaseModel):
    id: TaskId
    title: str
    status: TaskStatusEnum
    created_at: datetime


class ListTaskQueryParameters(PaginationSchema): ...
