from fastapi import APIRouter

from src.manager.config import ENVS
from src.modules.task.entrypoints.v1 import router as task_router

router = APIRouter(prefix=f"{ENVS.FASTAPI.ENDPOINT_PREFIX}")

router.include_router(router=task_router.app)
