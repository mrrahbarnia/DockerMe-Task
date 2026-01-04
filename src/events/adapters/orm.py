from datetime import datetime

import sqlalchemy.orm as so
from sqlalchemy.types import BIGINT
from sqlalchemy.dialects.postgresql import JSONB

from src.manager.common.db_metadata import BaseModel


class OutBoxEvent(BaseModel):
    __tablename__ = "outbox_events"
    id: so.Mapped[int] = so.mapped_column(BIGINT, primary_key=True, autoincrement=True)
    event_type: so.Mapped[str]
    payload: so.Mapped[dict] = so.mapped_column(JSONB)
    occurred_at: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now())
    processed: so.Mapped[bool] = so.mapped_column(default=False)
