"""API routers."""
from app.routers.auth import router as auth_router
from app.routers.deployment import router as deployment_router
from app.routers.generated_file import router as generated_file_router
from app.routers.pipeline import router as pipeline_router
from app.routers.project import router as project_router
from app.routers.run import router as run_router
from app.routers.user import router as user_router
from app.routers.validation import router as validation_router

__all__ = [
	"auth_router", "user_router", "project_router", "pipeline_router", "run_router",
	"validation_router", "deployment_router", "generated_file_router",
]
