from typing import List

from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import select

from .schema import UserFeedbacksTable
from api.schema import Review


class Dao:

    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker

    async def get_user_reviews(self, user_email):
        async with self._session_maker() as session:
            stmt = (
                select(UserFeedbacksTable)
                .where(UserFeedbacksTable.user_email == user_email)
                # .options(selectinload(UserFeedbacksTable.id))
            )
            result = await session.execute(stmt)
            return result.scalars()

    async def post_user_review(self, review: Review):
        async with self._session_maker() as session:
            async with session.begin():
                stmt = (
                    insert(UserFeedbacksTable)
                    .values(
                        id=review.id,
                        user_email=review.user_email,
                        place_uid=review.place_uid,
                        rate=review.rate,
                        feedback_text=review.feedback_text,
                    )
                    .returning(UserFeedbacksTable.id)
                )
                result = await session.execute(stmt)
                return result.scalar()
