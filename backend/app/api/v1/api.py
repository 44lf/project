from fastapi import APIRouter
from app.api.endpoints import auth, users, homework, corrections, reviews, dashboard

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(homework.router, prefix="/homework", tags=["作业"])
api_router.include_router(corrections.router, prefix="/corrections", tags=["批改"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["人工审核"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["学情分析"])
