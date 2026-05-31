from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, subscriptions, videos, clips, ai_jobs, usage_logs

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(clips.router, prefix="/clips", tags=["clips"])
api_router.include_router(ai_jobs.router, prefix="/ai-jobs", tags=["ai_jobs"])
api_router.include_router(usage_logs.router, prefix="/usage-logs", tags=["usage_logs"])
