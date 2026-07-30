import os
import sys
from pathlib import Path

# in-memory DB per test session; set BEFORE app imports read Settings
os.environ["NF_DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["NF_ENV"] = "dev"
os.environ["NF_AUTO_SEED"] = "true"

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import httpx
import pytest

from neuraforge.core.db import Base, engine
from neuraforge.interfaces.http import create_app


@pytest.fixture
async def client():
    # fresh schema per test: the module-level engine outlives each app instance
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    app = create_app()
    # ASGITransport doesn't run lifespan; trigger startup manually
    async with (
        httpx.ASGITransport(app=app) as transport,
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=transport, base_url="http://test") as c,
    ):
        yield c
