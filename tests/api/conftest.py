import pytest
from sqlalchemy import create_engine

from main import app


@pytest.fixture
async def api_client(aiohttp_client):
    client = await aiohttp_client(app)
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture
def migrated_postgres_connection(postgres):
    """
    Синхронное соединение со смигрированной БД.
    """
    engine = create_engine(postgres)
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()
        engine.dispose()
