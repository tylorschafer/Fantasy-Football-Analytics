from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import DATA_DIR, settings
from app.db import get_db
from app.models import League


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Fantasy Football League Analyzer API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/db/test")
async def test_database(db: AsyncSession = Depends(get_db)):
    """Test database connection by querying leagues."""
    result = await db.execute(select(League))
    leagues = result.scalars().all()
    return {
        "status": "connected",
        "database_url": settings.database_url,
        "league_count": len(leagues),
    }
