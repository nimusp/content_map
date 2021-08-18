from datetime import datetime
from http import HTTPStatus

import pytest

# from analyzer.db.schema import citizens_table, imports_table, relations_table
from utils.testing import (
    generate_place, get_places
)


datasets = [
    # Выгрузка с жителем, который сам себе родственник.
    # Обработчик должен возвращать идентификатор жителя в списке родственников.
    [
        generate_place()
    ],

    # Пустая выгрузка.
    # Обработчик не должен падать на пустой выгрузке.
    [],
]


@pytest.mark.parametrize('dataset', datasets)
async def test_get_places(api_client, dataset):
    query_params = {
        "latitude": 1,
        "longitude": 1,
        "zoom": 20,
        "state": "UGC",
    }
    places = await get_places(api_client, params=query_params)
    assert places == []
