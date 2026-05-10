import logging
from typing import Callable
from collections import defaultdict

from src.modules.shared.constant import Event, EVENT_REGISTRY, EventContext

logger = logging.getLogger(__name__)

EVENT_HANDLERS: dict[str, list[Callable]] = defaultdict(list)


def handler_register(event_type: type[Event]):
    def decorator(fn: Callable):
        event_name_string = event_type.__name__
        EVENT_HANDLERS[event_name_string].append(fn)

        return fn

    return decorator


async def handle_event(event_type: str, payload: dict, ctx: EventContext) -> None:
    handlers = EVENT_HANDLERS.get(event_type, [])

    event_cls = EVENT_REGISTRY.get(event_type)
    if not event_cls:
        logger.critical(f"Unknown event type: {event_type}")

    else:
        event = event_cls(**payload)

        for handler in handlers:
            await handler(event, ctx)
