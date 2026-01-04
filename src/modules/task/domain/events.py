from dataclasses import dataclass

from .types import TaskId
from src.manager.common.constants import Event


@dataclass(frozen=True)
class TaskRan(Event):
    id: TaskId
