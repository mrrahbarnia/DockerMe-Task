import random
from time import sleep
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from . import exceptions as exc
from .value_objects import TaskId, TaskStatusEnum
from .events import TaskRan
from src.modules.shared.constant import Entity, Event


@dataclass(unsafe_hash=True)
class Task(Entity):
    id: TaskId
    title: str
    status: TaskStatusEnum
    created_at: datetime
    events: list[Event] = field(
        default_factory=list, hash=False, init=False, compare=False
    )

    @staticmethod
    def create(title: str) -> "Task":
        return Task(
            id=TaskId(uuid4()),
            title=title,
            status=TaskStatusEnum.PENDING,
            created_at=datetime.now(timezone.utc),
        )

    def run(self) -> None:
        if self.status != TaskStatusEnum.PENDING:
            raise exc.TaskStatusIsNotPending
        self.status = TaskStatusEnum.RUNNING
        self.events.append(TaskRan(task_id=self.id))

    def process(self) -> None:
        # Blocking bussiness logic
        sleep(10)
        mocked_result = random.choice([-1, 1])
        if mocked_result == 1:
            self.status = TaskStatusEnum.DONE
        else:
            self.status = TaskStatusEnum.FAILED
