from dataclasses import dataclass

from .types import TaskId, TaskStatusEnum


@dataclass
class Task:
    id: TaskId
    title: str
    status: TaskStatusEnum
    # If we want to send some events
    # events:

    @staticmethod
    def create(id: TaskId, title: str) -> "Task":
        # We can publish an event for projection layer here.
        return Task(id=id, title=title, status=TaskStatusEnum.PENDING)
