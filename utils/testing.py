import random

from application.db_marshmallow_schemas import CourierSchema, PatchCourierSchema

from http import HTTPStatus
from random import choice, randint, randrange, shuffle
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union, Callable
import faker


fake = faker.Faker('ru_RU')
MAX_INTEGER = 2147483647


def generate_order(
        order_id: Optional[int] = None,
        weight: Optional[float] = None,
        regions: Optional[List[int]] = None,
        delivery_hours: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Создает и возвращает заказ, автоматически
    генерируя данные для не указанных полей
    """
    if order_id is None:
        order_id = randint(0, MAX_INTEGER)

    if weight is None:
        weight = round(random.uniform(0.1, 50), 2)

    if regions is None:
        regions = random.sample(range(1, 30), random.randint(1, 5))

    if delivery_hours is None:
        delivery_hours = generate_wh(
            randint(1, 5),
            [5 * 60, 15 * 60, 30 * 60, 60 * 60, 4 * 60 * 60]
        )

    return {
        'order_id': order_id,
        'weight': weight,
        'regions': regions,
        'delivery_hours': delivery_hours,
    }


def generate_courier(
        courier_id: Optional[int] = None,
        courier_type: Optional[str] = None,
        regions: Optional[List[int]] = None,
        working_hours: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Создает и возвращает курьера, автоматически
    генерируя данные для не указанных полей
    """
    if courier_id is None:
        courier_id = randint(0, MAX_INTEGER)

    if courier_type is None:
        courier_type = choice(('foot', 'bike', 'car'))

    if regions is None:
        regions = random.sample(range(1, 30), random.randint(1, 5))

    if working_hours is None:
        working_hours = generate_wh(
            randint(1, 5),
            [5 * 60, 15 * 60, 30 * 60, 60 * 60, 4 * 60 * 60]
        )

    return {
        'courier_id': courier_id,
        'courier_type': courier_type,
        'regions': regions,
        'working_hours': working_hours,
    }


def generate_couriers(
        couriers_num: int,
        **courier_kwargs
) -> List[Dict[str, Any]]:
    """
    Генерирует список курьеров

    parameters
    ----------
    couriers_num: int
        Количество курьеров
    courier_kwargs:
        Аргументы для функции generate_courier()
    """
    couriers = []
    for courier_id in range(couriers_num):
        couriers.append(
            generate_courier(courier_id=courier_id, **courier_kwargs)
        )
    return couriers


def add_leading_zero(num: int) -> str:
    """Добавляет ведущий ноль"""
    return f'0{num}' if num < 10 else str(num)


def seconds2time(seconds: int) -> str:
    """Превращает кол-во секунд в строку формата HH:MM"""
    hours = add_leading_zero(seconds // 3600 % 24)
    minutes = add_leading_zero(seconds // 60 % 60)
    return f'{hours}:{minutes}'


def generate_wh(qty: int, durations: List[int]) -> List[str]:
    """
    Генерация не пересекающихся временных
    интервалов (str) формата HH:MM-HH:MM
    Генерация происходит в пределах
    суток (86400 секунд)

    parameters
    ----------
    qty: int
        Кол-во интервалов для генерации
        **Примечание: (qty * max(durations)) < 86400
        Например, нельзя сгенерировать 25 временных интервалов,
        с продолжительностью 60 минут (3600 секунд) каждый, т.к.
        не хватит продолжительности суток: 25*3600 > 86400
    durations: List[int], int в секундах
        Длительность временного интервала
        **Если элементов в списке >1, выбирается
        случайное значение для каждой генерации
    """
    if not qty:
        # qty == 0
        return []
    wh: List[str] = []
    min_time = 0
    max_time = (86400 - 1) // qty

    temp = max_time
    for _ in range(qty):
        duration = random.choice(durations)

        start = random.randint(min_time, max_time - duration)
        end = start + duration

        time_interval = f'{seconds2time(start)}-{seconds2time(end)}'
        wh.append(time_interval)

        min_time = end
        max_time += temp
    return wh


def post_orders(
        client: Client,
        orders: List[Mapping[str, Any]],
        expected_status='201 CREATED',
        **request_kwargs
):# ) -> Optional[int]:
    response = client.post('/orders', json={"data": orders}, **request_kwargs)
    assert response.status == expected_status, response.json


def post_couriers(
        client: Client,
        couriers: List[Mapping[str, Any]],
        expected_status='201 CREATED',
        **request_kwargs
):# ) -> Optional[int]:
    response = client.post('/couriers', json={"data": couriers}, **request_kwargs)
    assert response.status == expected_status, response.json


def get_couriers(
        client: Client,
        expected_status=HTTPStatus.OK,
        **request_kwargs
) -> List[Dict[str, Any]]:
    response = client.get('/couriers', **request_kwargs)
    assert response.status == expected_status

    if response.status == '200 OK':
        data = response.json
        errors = CourierSchema(many=True).validate(data)
        assert errors == {}
        return sorted(data, key=lambda courier: courier['courier_id'])
