from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.config import settings
from app.database import init_db
from app.api.routes import router
from app.logging_config import setup_logging
import logging
import os

setup_logging()
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Self-Healing Framework database schema...")
    init_db()
    logger.info("Database schema initialized and ready.")
    yield
    logger.info("Shutting down Self-Healing Framework.")

app = FastAPI(
    title="An LLM-Based Self-Healing Framework for Reliable Multi-Step Task Automation",
    description="A multi-agent autonomous self-healing execution engine powered by Google Gemini and episodic memory.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Mount frontend production build if available
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    logger.info(f"Serving built React frontend from: {frontend_dist}")
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
