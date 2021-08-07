from typing import List

from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import select, insert

from .schema import UserFeedbacksTable
from api.schema import Feedback


class Dao:

    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker

    async def get_user_feedbacks(self, user_email):
        async with self._session_maker() as session:
            stmt = (
                select(UserFeedbacksTable)
                .where(UserFeedbacksTable.user_email == user_email)
            )
            result = await session.execute(stmt)
            return result.scalars()

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
                )
                result = await session.execute(stmt)
            return result.scalar()
