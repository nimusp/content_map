from data.schema import UsersTable

from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import select
from sqlalchemy.orm import selectinload


class Dao:

    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker

    async def get_user_model(self, user_email: str):
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
