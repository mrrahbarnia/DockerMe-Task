from typing import Sequence
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from .db_models import OutBoxEvent

from src.modules.shared.constant import DBLock


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, event_type: str, payload: dict) -> None:
        stmt = sa.insert(OutBoxEvent).values(
            {OutBoxEvent.event_type: event_type, OutBoxEvent.payload: payload}
        )
        await self.session.execute(stmt)

    async def fetch_unprocessed(
        self, limit: int, lock: DBLock = DBLock(is_active=False)
    ) -> Sequence[OutBoxEvent]:
        await self.session.execute(sa.text("SET LOCAL lock_timeout = '2s'"))
        stmt = (
            sa.select(OutBoxEvent)
            .where(
                sa.and_(
                    OutBoxEvent.is_processed.is_(False),
                    OutBoxEvent.processing_error.is_(None),
                    OutBoxEvent.next_retry_at < datetime.now(timezone.utc),
                )
            )
            .limit(limit)
        )
        if lock.is_active:
            await self.session.execute(
                sa.text(f"SET LOCAL lock_timeout = '{lock.timeout_second}s'")
            )
            stmt = stmt.with_for_update(skip_locked=lock.skip_locked)

        try:
            return (await self.session.scalars(stmt)).all()
        except Exception:
            return []

    async def mark_processed(self, id: int) -> None:
        stmt = (
            sa.update(OutBoxEvent)
            .values(
                {
                    OutBoxEvent.is_processed: True,
                    OutBoxEvent.processed_at: datetime.now(),
                }
            )
            .where(OutBoxEvent.id == id)
        )
        await self.session.execute(stmt)

    async def get_by_id(
        self, id: int, lock: DBLock = DBLock(is_active=False)
    ) -> OutBoxEvent | None:
        stmt = sa.select(OutBoxEvent).where(OutBoxEvent.id == id).limit(1)
        if lock.is_active:
            await self.session.execute(
                sa.text(f"SET LOCAL lock_timeout = '{lock.timeout_second}s'")
            )
            stmt = stmt.with_for_update(skip_locked=lock.skip_locked)
        try:
            return await self.session.scalar(stmt)
        except Exception:
            return None

    async def schedule_retry(self, id: int, next_retry_at: datetime) -> None:
        stmt = (
            sa.update(OutBoxEvent)
            .values(
                {
                    OutBoxEvent.retry_attempt: OutBoxEvent.retry_attempt + 1,
                    OutBoxEvent.next_retry_at: next_retry_at,
                    OutBoxEvent.last_attempted_at: datetime.now(),
                }
            )
            .where(OutBoxEvent.id == id)
        )
        await self.session.execute(stmt)

    async def mark_dead(self, id: int, processing_error: str) -> None:
        stmt = (
            sa.update(OutBoxEvent)
            .values(
                {
                    OutBoxEvent.processing_error: processing_error,
                    OutBoxEvent.retry_attempt: OutBoxEvent.retry_attempt + 1,
                    OutBoxEvent.last_attempted_at: datetime.now(),
                }
            )
            .where(OutBoxEvent.id == id)
        )
        await self.session.execute(stmt)
