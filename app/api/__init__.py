from fastapi import APIRouter
from api.websockets import router as ws_router

router = APIRouter()
router.include_router(ws_router)