from typing import NewType
from uuid import UUID
from enum import StrEnum, auto

TaskId = NewType("TaskId", UUID)


class TaskStatusEnum(StrEnum):
    PENDING = auto()
    RUNNING = auto()
    DONE = auto()
    FAILED = auto()
