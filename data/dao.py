from typing import List

from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import select


class FamilyMemberDTO:

    def __init__(self, id: int, nickname: str) -> None:
        self.id = id
        self.nickname = nickname


class Dao:

    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker
