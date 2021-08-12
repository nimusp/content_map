import http
from typing import Union, Optional
from http import HTTPStatus
from enum import Enum, unique

from aiohttp import web
from aiohttp_pydantic.oas.typing import r200, r201, r404


from api.base_view import BaseView
from api.schema import (
    GetVisitedPlacesResponse, Place,
    CommonError,
)
from data.schema import UsersTable, PlacesTable, user_places


@unique
class MapContext(Enum):
    default = 'DEFAULT'
    ugc = 'UGC'


class ViewportCoords(BaseView):
    async def get(
            self, user_email: str,
            longitude: float,
            latitude: float,
            zoom: float,
            context: MapContext
    ) -> Union[r200[GetVisitedPlacesResponse], r404[CommonError]]:

        model = await self.dao.get_user_model(user_email)
        if not model.visited_places:
            return web.json_response(
                CommonError(error_message='Нет мест').dict(),
                status=http.HTTPStatus.NOT_FOUND
            )


