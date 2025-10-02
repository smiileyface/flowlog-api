from fastapi import APIRouter

from app.api.v1.ai_jobs import router as ai_jobs_router
from app.api.v1.journals import router as journals_router
from app.api.v1.notes import router as notes_router
from app.api.v1.projects import router as projects_router
from app.api.v1.tags import router as tags_router

# Create v1 API router
api_router = APIRouter()

# Include all v1 endpoint routers
api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
api_router.include_router(journals_router, prefix="/journals", tags=["Journals"])
api_router.include_router(notes_router, prefix="/notes", tags=["Notes"])
api_router.include_router(tags_router, prefix="/tags", tags=["Tags"])
api_router.include_router(ai_jobs_router, prefix="/ai-jobs", tags=["AI Jobs"])
