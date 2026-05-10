from dataclasses import dataclass
from uuid import uuid4, UUID

from .value_objects import TaskId

from src.modules.shared.constant import Event


@dataclass(frozen=True)
class TaskRan(Event):
    task_id: TaskId
    event_id: UUID = uuid4()
