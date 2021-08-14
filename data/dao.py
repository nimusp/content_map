from typing import Optional, Union, Tuple, Collection
from dataclasses import dataclass
import re

from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import select, join, func, and_, between
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound

from data.schema import UserFeedbacksTable
from data.schema import UsersTable, PlacesTable, user_places
from api.schema import Feedback, Place, GetVisitedPlacesResponse, ScreenResolution
from utils.emulator_specifications import EMULATOR_SCREEN, K_DICT


def get_screen_coordinate_bounds(
        device: ScreenResolution,
        latitude: float,
        longitude: float,
        zoom: float,
) -> Tuple[float]:
    """
    Получить примерные географические
    координаты возле углов viewport'a

    :param device:
        Разрешение экрана в пикселях

    :param latitude:
        Центральная координата экрана, широта
    :param longitude:
        Центральная координата экрана, долгота

    :param zoom:
        Текущее значение приближения карты в приложении

    :return:
        Кортеж с граничными географическими значениями в формате:
        (tl_lat, tl_lon, br_lat, br_lon)
        **tl, br == top-left, bottom-right
    """
    zoom_float = zoom
    zoom_int = int(zoom_float)
    zoom_mod = 1 - (zoom_float % 1)

    # sr == screen resolution
    k_height_sr = device.height / EMULATOR_SCREEN.height
    k_width_sr = device.width / EMULATOR_SCREEN.width

    lat_quarter = (K_DICT[zoom_int]['lat_delta'] * k_height_sr) / 4
    lon_quarter = (K_DICT[zoom_int]['lon_delta'] * k_width_sr) / 4

    lat_additional = lat_quarter + (lat_quarter * zoom_mod)
    lon_additional = lon_quarter + (lon_quarter * zoom_mod)

    # Screen coordinate bounds
    # tl == top-left, br == bottom-right
    tl_lat = latitude + lat_additional
    tl_lon = longitude - lon_additional

    br_lat = latitude - lat_additional
    br_lon = longitude + lon_additional
    return tl_lat, tl_lon, br_lat, br_lon


class Dao:

    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker

    async def get_user_model(self, user_email: str) -> UsersTable:
        async with self._session_maker() as session:
            query = select(UsersTable) \
                .where(UsersTable.email == user_email) \
                .options(
                selectinload(UsersTable.visited_places),
                selectinload(UsersTable.feedbacks),
            )

            result = await session.execute(query)
            user = result.scalars().one()
            return user

    async def get_visited_places(
            self,
            email: str,
            latitude: float,
            longitude: float,
            zoom: float,
            device: ScreenResolution,
    ):
        """
        Получение посещенных мест
        в границах viewport'а пользователя

        :param email:
            email пользователя

        :param latitude:
            Центральная координата экрана, широта
        :param longitude:
            Центральная координата экрана, долгота

        :param zoom:
            Текущее значение приближения карты в приложении

        :param device:
            Разрешение экрана в пикселях

        :return:
        """
        async with self._session_maker() as session:
            srid = 4326
            wkt_point = f'POINT({longitude} {latitude})'

            # lb, up == lower and upper bounds
            lat_ub, lon_lb, lat_lb, lon_ub = (
                get_screen_coordinate_bounds(
                    device=device,
                    latitude=latitude,
                    longitude=longitude,
                    zoom=zoom
                )
            )

            uids = (
                select([user_places.c.place_uid])
                .where(user_places.c.user_email == email)
            )
            uids_without_feedback = (
                select([uids.c.place_uid])
                .select_from(
                    join(uids, UserFeedbacksTable,
                         uids.c.place_uid == UserFeedbacksTable.place_uid,
                         isouter=True)
                )
                .where(UserFeedbacksTable.place_uid == None)
            )
            stmt = (
                select([
                    PlacesTable.uid,
                    PlacesTable.id,
                    func.ST_X(PlacesTable.coordinates).label('x'),
                    func.ST_Y(PlacesTable.coordinates).label('y')
                ])
                .select_from(
                    join(
                        PlacesTable, uids_without_feedback,
                        PlacesTable.uid == uids_without_feedback.c.place_uid,
                    )
                )
                .where(
                    and_(
                        between(func.ST_X(PlacesTable.coordinates), lon_lb, lon_ub),
                        between(func.ST_Y(PlacesTable.coordinates), lat_lb, lat_ub),
                    )
                )
                .order_by(
                    func.ST_Distance(
                        func.ST_GeomFromText(wkt_point, srid),
                        PlacesTable.coordinates
                    )
                )
            )

            result = await session.execute(stmt)
            # for row in result.fetchall():
            #     print(row.distance, row.x, row.y)
            return result

    async def add_user_places(self, user_email: str, place: PlacesTable):
        async with self._session_maker() as session:
            async with session.begin():
                query = insert(UsersTable) \
                    .values(email=user_email) \
                    .on_conflict_do_nothing()

                await session.execute(query)

                query = insert(PlacesTable). \
                    values(
                    uid=place.uid,
                    id=place.id,
                    coordinates=place.coordinates
                ).on_conflict_do_nothing()

                await session.execute(query)

                query = insert(user_places) \
                    .values(user_email=user_email, place_uid=place.uid) \
                    .on_conflict_do_nothing()

                await session.execute(query)

    async def get_user_feedbacks(self, user_email):
        async with self._session_maker() as session:
            stmt = (
                select(UserFeedbacksTable)
                .where(UserFeedbacksTable.user_email == user_email)
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    async def post_user_feedback(self, feedback: Feedback):
        async with self._session_maker() as session:
            async with session.begin():
                stmt = (
                    insert(UserFeedbacksTable)
                    .values(
                        user_email=feedback.user_email,
                        place_uid=feedback.place_uid,
                        rate=feedback.rate,
                        feedback_text=feedback.feedback_text,
                    )
                    .returning(UserFeedbacksTable.id)
                    .on_conflict_do_update(
                        index_elements=['user_email', 'place_uid'],
                        set_=dict(rate=feedback.rate, feedback_text=feedback.feedback_text),
                    )
                )
                result = await session.execute(stmt)
            return result.scalar()
