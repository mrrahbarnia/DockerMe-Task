from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.types import BIGINT
from sqlalchemy.dialects.postgresql import JSONB

from src.modules.shared.infrastructure.db_metadata import BaseModel


class OutBoxEvent(BaseModel):
    __tablename__ = "outbox_events"
    id: so.Mapped[int] = so.mapped_column(BIGINT, primary_key=True, autoincrement=True)
    event_type: so.Mapped[str]
    payload: so.Mapped[dict] = so.mapped_column(JSONB)
    processed_at: so.Mapped[datetime | None]
    processing_error: so.Mapped[str | None] = so.mapped_column(sa.Text)
    last_attempted_at: so.Mapped[datetime | None]
    next_retry_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now()
    )
    is_processed: so.Mapped[bool] = so.mapped_column(default=False)
    retry_attempt: so.Mapped[int] = so.mapped_column(default=0)
    created_at: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now())
