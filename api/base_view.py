from aiohttp_pydantic import PydanticView

from data.dao import Dao


DB_KEY = 'db_conn'


class BaseView(PydanticView):

    @property
    def dao(self) -> Dao:
        return self.request.app[DB_KEY]
