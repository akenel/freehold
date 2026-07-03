"""Freehold — the async database engine + session factory.

The app talks to Postgres asynchronously (asyncpg). Migrations run separately,
synchronously, via Alembic (see alembic/). One DATABASE_URL feeds both — we just
swap the driver.
"""
import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from models import Base  # noqa: F401  (re-exported for convenience)


def _async_url() -> str:
    url = os.getenv("DATABASE_URL", "")
    if url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    return url


engine = create_async_engine(_async_url(), echo=False, pool_pre_ping=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
