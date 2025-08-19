from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.database import Base, engine
from src.routers import auth, snippets, run, history

# Initialize DB schema at startup (for SQLite default). In production, use migrations.
Base.metadata.create_all(bind=engine)

settings = get_settings()

# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance with routes, CORS, and docs metadata.
    """
    app = FastAPI(
        title="Python Playground API",
        description="Secure Python code execution with snippets, history, and user authentication.",
        version="1.0.0",
        openapi_tags=[
            {"name": "Health", "description": "Service status checks."},
            {"name": "Auth", "description": "User registration, login, and authentication."},
            {"name": "Snippets", "description": "Create, read, update, delete code snippets."},
            {"name": "Run", "description": "Execute Python code securely with limits."},
            {"name": "History", "description": "Execution history for users."},
        ],
    )

    # CORS configuration from environment
    allow_origins: List[str] = settings.CORS_ALLOW_ORIGINS.split(",") if settings.CORS_ALLOW_ORIGINS else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in allow_origins if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth.router, prefix="/auth", tags=["Auth"])
    app.include_router(snippets.router, prefix="/snippets", tags=["Snippets"])
    app.include_router(run.router, prefix="/run", tags=["Run"])
    app.include_router(history.router, prefix="/history", tags=["History"])

    # Health endpoint
    @app.get("/", tags=["Health"], summary="Health Check", description="Simple health check endpoint.")
    # PUBLIC_INTERFACE
    def health_check():
        """Return a simple health status message."""
        return {"message": "Healthy"}

    return app


# FastAPI ASGI app instance
app = create_app()
