from typing import Annotated
from fastapi import APIRouter, status, Depends

# from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas, http_exceptions
from .http_response import HTTPResponse
from ..dependencies import get_uow, get_session
from ...service import queries, commands
# from ...service.unit_of_work import SqlAlchemyUnitOfWork
# from ...domain.models import BookAlreadyBorrowedExc, BookNotBorrowedExc
# from src.manager.common.types import BookID
# from src.manager.common.pagination_schema import (
#     PaginationResponse,
#     PaginationResponseSchema,
# )

app = APIRouter(prefix="/v1/tasks", tags=["tasks"])


@app.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_task(): ...


@app.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(): ...


@app.get("", status_code=status.HTTP_200_OK)
async def list_tasks(): ...


@app.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task(): ...
