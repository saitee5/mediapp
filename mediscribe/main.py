import os
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the mediscribe root and src directory to Python sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils.config import settings
from src.utils.logger import logger
from src.api.routes import router as api_router

def create_app() -> FastAPI:
    """FastAPI Application factory for MediScribe AI Agent."""
    app = FastAPI(
        title="MediScribe AI Agent API",
        description="Clinical speech-to-text, SOAP extraction, and patient case sheet generation AI agent",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Enable CORS for frontend clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router)

    @app.get("/", include_in_schema=False)
    async def root_redirect():
        """Redirects root access to interactive Swagger UI documentation."""
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/docs")

    @app.on_event("startup")
    async def startup_event():
        logger.info("=" * 60)
        logger.info(f"MediScribe AI Agent server is ONLINE!")
        logger.info(f"Interactive Swagger UI : http://localhost:{settings.PORT}/docs")
        logger.info(f"ReDoc Documentation    : http://localhost:{settings.PORT}/redoc")
        logger.info(f"Health Check           : http://localhost:{settings.PORT}/api/health")
        logger.info("=" * 60)

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("MediScribe AI Agent server shutting down...")

    return app


app = create_app()

if __name__ == "__main__":
    port = settings.PORT
    host = settings.HOST
    logger.info(f"Starting server on http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=settings.DEBUG)
