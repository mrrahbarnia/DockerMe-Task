from dataclasses import dataclass

from ..infrastructure.unit_of_work import UOW


@dataclass
class EventContext:
    uow: UOW
