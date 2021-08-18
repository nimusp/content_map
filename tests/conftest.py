import os
import uuid

import pytest
from sqlalchemy_utils import create_database, drop_database
from yarl import URL


PG_URL = os.getenv('CI_ANALYZER_PG_URL', 'postgresql+asyncpg://postgres:123@localhost:5432/map_content')


@pytest.fixture
def postgres():
    """
    Создает временную БД для запуска теста.
    """
    tmp_name = '.'.join([uuid.uuid4().hex, 'pytest'])
    tmp_url = str(URL(PG_URL).with_path(tmp_name))
    create_database(tmp_url)

    try:
        yield tmp_url
    finally:
        drop_database(tmp_url)

