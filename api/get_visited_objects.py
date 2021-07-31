from aiohttp import web
from http import HTTPStatus
from aiohttp_pydantic.oas.typing import r200

from api.base_view import BaseView

from api.schema import GetVisitedObjectsResponse, Place


class GetVisitedObjects(BaseView):

    async def get(self, user_id: int) -> r200[GetVisitedObjectsResponse]:
        return web.json_response(
            GetVisitedObjectsResponse(
                places=[
                    Place(geo_id=1, latitude=55.733842, longitude=37.588144), 
                    Place(geo_id=2, with_feedback=True, latitude=55.729948, longitude=37.601736),
                ],
            ).dict(), 
            status=HTTPStatus.OK)