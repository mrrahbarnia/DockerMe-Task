from uuid import uuid4
from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so

from ..domain.types import TaskId, TaskStatusEnum
from src.manager.common.db_metadata import BaseModel


class Task(BaseModel):
    __tablename__ = "tasks"
    title: so.Mapped[str] = so.mapped_column(sa.String(250))
    status: so.Mapped[TaskStatusEnum] = so.mapped_column(
        sa.Enum(TaskStatusEnum), default=TaskStatusEnum.PENDING
    )
    created_at: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now())
    id: so.Mapped[TaskId] = so.mapped_column(primary_key=True, default=lambda: uuid4())
