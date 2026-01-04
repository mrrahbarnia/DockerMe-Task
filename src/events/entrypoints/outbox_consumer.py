import asyncio
import logging

from ..service.unit_of_work import IUnitOfWork, SqlAlchemyUnitOfWork
from ..service.messagebus import handle_event
from ..bootstrap import bootstrap

logger = logging.getLogger(__name__)


async def process_event(uow: IUnitOfWork) -> None:
    # In production we have to processing events in bulk(for example each time we can fetch 50 events)
    async with uow:
        unprocessed_event = await uow.events.fetch_unprocessed()

        if unprocessed_event:
            try:
                await handle_event(
                    event_type=unprocessed_event.event_type,
                    payload=unprocessed_event.payload,
                )
            except Exception as ex:
                logger.critical(ex)
                # We can implement Retry logic here
                raise
            else:
                await uow.events.mark_processed(event_id=unprocessed_event.id)


async def main() -> None:
    sqlalchemy_uow = SqlAlchemyUnitOfWork()
    while True:
        await process_event(uow=sqlalchemy_uow)
        await asyncio.sleep(1)


if __name__ == "__main__":
    bootstrap()
    asyncio.run(main())
