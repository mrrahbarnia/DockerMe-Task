import logging
from typing import Annotated

from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas, http_exceptions
from .http_response import HTTPResponse
from ..dependencies import get_uow
from ...domain import exceptions as domain_exc
from ...domain.value_objects import TaskId
from ...service import queries, commands, exceptions as service_exc

from src.modules.shared.dependencies import get_session
from src.modules.shared.infrastructure.unit_of_work import UOW
from src.modules.shared.constant import (
    PaginationResponse,
    PaginationResponseSchema,
)

logger = logging.getLogger(__name__)

app = APIRouter(prefix="/v1/tasks", tags=["tasks"])


@app.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=HTTPResponse[schemas.CreateTaskResponse],
)
async def create_task(
    payload: schemas.CreateTaskRequest,
    uow: Annotated[UOW, Depends(get_uow)],
) -> HTTPResponse[schemas.CreateTaskResponse]:
    try:
        created_task = await commands.create_task(uow=uow, title=payload.title)
        return HTTPResponse[schemas.CreateTaskResponse](
            success=True,
            message="Task created successfully",
            data=schemas.CreateTaskResponse(
                id=created_task.id,
                title=created_task.title,
            ),
        )
    except Exception as ex:
        raise http_exceptions.ServerError(data=str(ex))


@app.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task_id: TaskId,
    uow: Annotated[UOW, Depends(get_uow)],
):
    try:
        await commands.delete_task(uow=uow, task_id=task_id)

    except service_exc.EntityNotFound:
        raise http_exceptions.EntityNotFoundException(data={"task_id": str(task_id)})

    except Exception as ex:
        logger.error(ex)
        raise http_exceptions.ServerError(data=str(ex))


@app.post(
    "/{task_id}/run",
    status_code=status.HTTP_200_OK,
    response_model=HTTPResponse[schemas.DetailTaskResponse],
)
async def run_task(
    task_id: TaskId, uow: Annotated[UOW, Depends(get_uow)]
) -> HTTPResponse[schemas.DetailTaskResponse]:
    try:
        task = await commands.run_task(uow=uow, task_id=task_id)
        return HTTPResponse[schemas.DetailTaskResponse](
            success=True,
            message="Task ran successfully.",
            data=schemas.DetailTaskResponse(
                id=task.id,
                title=task.title,
                status=task.status,
                created_at=task.created_at,
            ),
        )

    except service_exc.EntityNotFound:
        raise http_exceptions.EntityNotFoundException(data={"task_id": str(task_id)})

    except domain_exc.TaskStatusIsNotPending as ex:
        logger.warning(ex)
        raise http_exceptions.BadRequestException(
            data={"task_id": str(task_id)}, message="Task is not in PENDING status."
        )

    except Exception as ex:
        logger.error(ex)
        raise http_exceptions.ServerError(data=str(ex))


@app.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=PaginationResponseSchema[list[schemas.DetailTaskResponse]],
)
async def list_tasks(
    query_parameters: Annotated[schemas.ListTaskQueryParameters, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PaginationResponseSchema[list[schemas.DetailTaskResponse]]:
    try:
        limit, offset = query_parameters.to_limit_offset()
        tasks, count = await queries.get_task_list(
            session=session,
            limit=limit,
            offset=offset,
            sort_mode=query_parameters.sort_mode,
        )
        return PaginationResponseSchema[list[schemas.DetailTaskResponse]](
            data=[
                schemas.DetailTaskResponse(
                    id=t.id, title=t.title, status=t.status, created_at=t.created_at
                )
                for t in tasks
            ],
            pagination=PaginationResponse(
                current_page=query_parameters.page_number,
                page_size=query_parameters.page_size,
                total=count if count else 0,
            ),
        )

    except Exception as ex:
        logger.error(ex)
        raise http_exceptions.ServerError(data=str(ex))


@app.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=HTTPResponse[schemas.DetailTaskResponse],
)
async def get_task(
    task_id: TaskId,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> HTTPResponse[schemas.DetailTaskResponse]:
    try:
        task = await queries.get_task_detail(task_id=task_id, session=session)
        return HTTPResponse[schemas.DetailTaskResponse](
            success=True,
            message="Task fetched successfully.",
            data=schemas.DetailTaskResponse(
                id=task.id,
                title=task.title,
                status=task.status,
                created_at=task.created_at,
            ),
        )

    except service_exc.EntityNotFound:
        raise http_exceptions.EntityNotFoundException(data={"task_id": str(task_id)})

    except Exception as ex:
        logger.error(ex)
        raise http_exceptions.ServerError(data=str(ex))
