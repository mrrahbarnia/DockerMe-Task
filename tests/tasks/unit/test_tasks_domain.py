from uuid import uuid4
from datetime import datetime

import pytest

from src.modules.task.domain import models, exceptions, types, events


async def test_run_function_with_invalid_state():
    task = models.Task(
        id=types.TaskId(uuid4()),
        title="Sample Task",
        status=types.TaskStatusEnum.DONE,
        created_at=datetime.now(),
    )
    with pytest.raises(exceptions.TaskStatusIsNotPending):
        task.run()


async def test_send_taskran_event_successfully():
    task = models.Task(
        id=types.TaskId(uuid4()),
        title="Sample Task",
        status=types.TaskStatusEnum.PENDING,
        created_at=datetime.now(),
    )
    task.run()

    assert any(isinstance(event, events.TaskRan) for event in task.events)
    assert len(task.events) == 1
    assert task.status == types.TaskStatusEnum.RUNNING
