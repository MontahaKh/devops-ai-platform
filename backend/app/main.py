from fastapi import FastAPI

from app.core.config import settings
from app.models import User, Project  # noqa: F401 - Import for SQLAlchemy metadata
from app.routers import (
    auth_router,
    deployment_router,
    generated_file_router,
    pipeline_router,
    project_router,
    run_router,
    user_router,
    validation_router,
)


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(pipeline_router)
app.include_router(run_router)
app.include_router(validation_router)
app.include_router(deployment_router)
app.include_router(generated_file_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}