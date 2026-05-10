import logging
from datetime import datetime, timezone, timedelta

from ..service.messagebus import handle_event

from src.core.config import ENVS
from src.modules.shared.constant import DBLock, EventContext

logger = logging.getLogger(__name__)


async def process_event(ctx: EventContext) -> None:
    uow = ctx.uow
    async with uow:
        unprocessed_event = await uow.outbox.fetch_unprocessed(
            limit=1, lock=DBLock(is_active=True, timeout_second=2, skip_locked=True)
        )

    if unprocessed_event:
        for event in unprocessed_event:
            try:
                await handle_event(
                    event_type=event.event_type, payload=event.payload, ctx=ctx
                )
            except Exception as ex:
                logger.critical(f"Error processing event {event.id}: {ex}")
                async with uow:
                    if event.retry_attempt < ENVS.OUTBOX.MAX_RETRIES:
                        # TODO: We can add Jitter here
                        delay = ENVS.OUTBOX.BACKOFF_SEC * (
                            2 ** (event.retry_attempt - 1)
                        )
                        next_retry_at = datetime.now(timezone.utc) + timedelta(
                            seconds=delay
                        )
                        await uow.outbox.schedule_retry(
                            id=event.id, next_retry_at=next_retry_at
                        )
                    else:
                        await uow.outbox.mark_dead(
                            id=event.id, processing_error=str(ex)
                        )
                        pass
            else:
                async with uow:
                    await uow.outbox.mark_processed(id=event.id)
