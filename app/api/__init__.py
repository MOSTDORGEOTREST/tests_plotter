from fastapi import APIRouter
from api.websockets import router as ws_router
from api.experiments import router as experiments_router

router = APIRouter()
router.include_router(ws_router)
router.include_router(experiments_router)