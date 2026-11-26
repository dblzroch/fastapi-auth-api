"""Pytest configuration and fixtures."""

from typing import AsyncGenerator, Any

import asyncio

import pytest
from authapi.database import Base, async_session, engine


@pytest.fixture
def event_loop() -> Any:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
async def init_db() -> AsyncGenerator[None, None]:
    """Create all database tables before tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(init_db: Any) -> AsyncGenerator[Any, None]:
    """Provide a transactional database session for tests."""
    async with async_session() as session:
        yield session
        await session.rollback()
