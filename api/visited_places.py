from aiohttp import web
from http import HTTPStatus
from aiohttp_pydantic.oas.typing import r200

from api.base_view import BaseView

from api.schema import GetVisitedPlacesResponse, Place


class VisitedPlaces(BaseView):

    async def get(self, user_email: int) -> r200[GetVisitedPlacesResponse]:
        return web.json_response(
            GetVisitedPlacesResponse(
                places=[
                    Place(uid='aaa', latitude=55.733842, longitude=37.588144), 
                    Place(uid='bbb', with_feedback=True, latitude=55.729948, longitude=37.601736),
                ],
            ).dict(), 
            status=HTTPStatus.OK)
