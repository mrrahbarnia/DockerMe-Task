from dataclasses import dataclass, field
from datetime import datetime, timezone

from . import exceptions as exc
from .types import TaskId, TaskStatusEnum
from .events import TaskRan
from src.manager.common.constants import Event


@dataclass
class Task:
    id: TaskId
    title: str
    status: TaskStatusEnum
    created_at: datetime
    events: list[Event] = field(default_factory=list)

    @staticmethod
    def create(id: TaskId, title: str) -> "Task":
        return Task(
            id=id,
            title=title,
            status=TaskStatusEnum.PENDING,
            created_at=datetime.now(timezone.utc),
        )

    def run(self):
        if self.status != TaskStatusEnum.PENDING:
            raise exc.TaskStatusIsNotPending
        self.status = TaskStatusEnum.RUNNING
        self.events.append(TaskRan(id=self.id))
