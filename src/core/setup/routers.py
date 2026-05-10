from fastapi import APIRouter

from src.core.config import ENVS
from src.modules.shared.health_check import router as health_check_router
from src.modules.task.entrypoints.v1 import router as task_router

router = APIRouter(prefix=f"{ENVS.FASTAPI.ENDPOINT_PREFIX}")

router.include_router(router=health_check_router)
router.include_router(router=task_router.app)
