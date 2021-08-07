from data.schema import UsersTable, PlacesTable, user_places

from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload


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

    async def add_user_places(self, user_email: str, place: PlacesTable):
        async with self._session_maker() as session:
            async with session.begin():
                query = insert(UsersTable).\
                    values(email=user_email)\
                    .on_conflict_do_nothing()

                await session.execute(query)

                query = insert(PlacesTable). \
                    values(
                    uid=place.uid,
                    latitude=place.latitude,
                    longitude=place.longitude
                ).on_conflict_do_nothing()

                await session.execute(query)

                query = insert(user_places).\
                    values(user_email=user_email, place_uid=place.uid).\
                    on_conflict_do_nothing()

                await session.execute(query)

