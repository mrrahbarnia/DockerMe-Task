import logging
from typing import TypeVar, Generic

from pydantic import BaseModel
from sqlalchemy import text
from fastapi import APIRouter, status

from .constant import Environment
from .infrastructure.db_metadata import ASYNC_ENGINE

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/check-infrastructure", tags=["HEALTH-CHECK"])

T = TypeVar("T")


class HTTPResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None


class CheckInfraResponse(BaseModel):
    postgresql_connection: str | None = None


@router.get("", status_code=status.HTTP_200_OK, response_model_exclude_none=True)
async def check_infrastructure() -> (
    HTTPResponse[CheckInfraResponse] | HTTPResponse[None]
):
    result = {}

    # ================ Check PostgreSQL
    try:
        async with ASYNC_ENGINE.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as ex:
        logger.critical(f"Postgres connection failed: {ex}")
        result["postgresql_connection"] = (
            str(ex) if Environment.DEVELOPMENT else "Something went wrong"
        )

    if not result:
        return HTTPResponse[None](success=True, message="OK", data=None)
    else:
        return HTTPResponse[CheckInfraResponse](
            success=False,
            message="Something went wrong",
            data=CheckInfraResponse(**result),
        )
