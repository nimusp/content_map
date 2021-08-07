from data.schema import UsersTable, PlacesTable, user_places

from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from data.schema import UserFeedbacksTable
from api.schema import Feedback


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
                query = insert(UsersTable) \
                    .values(email=user_email) \
                    .on_conflict_do_nothing()

                await session.execute(query)

                query = insert(PlacesTable). \
                    values(
                        uid=place.uid,
                        latitude=place.latitude,
                        longitude=place.longitude
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
            stmt = (
                insert(UserFeedbacksTable)
                .values(
                    user_email=feedback.user_email,
                    place_uid=feedback.place_uid,
                    rate=feedback.rate,
                    feedback_text=feedback.feedback_text,
                )
                .returning(UserFeedbacksTable.id)
            )
            result = await session.execute(stmt)
            return result.scalar()
