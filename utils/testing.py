import random
import time
import uuid
from typing import Tuple
from enum import EnumMeta

# from application.db_marshmallow_schemas import CourierSchema, PatchCourierSchema

from http import HTTPStatus
from random import choice, randint, randrange, shuffle
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union, Callable
from faker import Faker
from aiohttp.test_utils import TestClient


fake = Faker('ru_RU')


def generate_place(
        user_email: Optional[str] = None,
        place_uid: Optional[str] = None,
        place_id: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
) -> Dict[str, Any]:
    """
    Создает и возвращает место где побывал пользователь,
    автоматически генерируя данные для не указанных полей
    """
    if user_email is None:
        user_email = fake.email()

    if place_uid is None:
        place_uid = '.'.join([uuid.uuid4().hex, str(time.time())])

    if place_id is None:
        place_id = random.randint(1, 100)

    if latitude is None:
        latitude = fake.latitude()

    if longitude is None:
        longitude = fake.longitude()
    return locals()


def generate_couriers(
        qty: int,
        **place_kwargs
) -> Tuple[Dict[str, Any]]:
    """
    Генерирует список курьеров

    parameters
    ----------
    qty: int
        Количество мест
    **place_kwargs:
        Аргументы для функции generate_place()
    """
    return tuple(
        (generate_place(**place_kwargs)
         for _ in range(qty))
    )


async def get_places(
        client: TestClient,
        expected_status: Union[int, EnumMeta] = HTTPStatus.OK,
        **request_kwargs
) -> List[dict]:
    response = await client.get(
        '/visited_places',
        **request_kwargs
    )
    assert response.status == expected_status

    if response.status == HTTPStatus.OK:
        data = await response.json()
        # errors = CitizensResponseSchema().validate(data)
        # assert errors == {}
        return data


# async def post_places(
#         client: TestClient,
#         places,
#         expected_status: Union[int, EnumMeta] = HTTPStatus.OK,
#         **request_kwargs
# ) -> List[dict]:
#     response = await client.post(
#         '/visited_places',
#         json=places,
#         **request_kwargs
#     )
#     assert response.status == expected_status
#
#     if response.status == HTTPStatus.OK:
#         data = await response.json()
#         # errors = CitizensResponseSchema().validate(data)
#         # assert errors == {}
#         return data