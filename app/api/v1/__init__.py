from fastapi import APIRouter

from app.api.v1.router import router as v1_router
from app.api.v1.routes_analysis import router as analysis_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(v1_router, tags=["health"])
api_v1_router.include_router(analysis_router, tags=["analysis"])
