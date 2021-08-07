from aiohttp import web
from http import HTTPStatus
from aiohttp_pydantic.oas.typing import r200, r201, r400, r404
from pydantic.typing import Union
from sqlalchemy.exc import NoResultFound

from api.base_view import BaseView

from api.schema import GetVisitedPlacesResponse, CommonError, Place, AddVisitedPlacesRequest, AddVisitedPlacesResponse
from data.schema import UsersTable, PlacesTable


class VisitedPlaces(BaseView):

    async def get(self, user_email: str) -> Union[r200[GetVisitedPlacesResponse], r404[CommonError]]:
        user_model: UsersTable = None
        try:
            user_model = await self.dao.get_user_model(user_email)
        except NoResultFound as ex:
            pass
            # TODO: log exception

        if not user_model or len(user_model.visited_places) == 0:
            return web.json_response(
                CommonError(
                    error_message=f'no data for user with email {user_email}'
                ).dict(), status=HTTPStatus.NOT_FOUND
            )

        places_with_feedback = set()
        for feedback in user_model.feedbacks:
            places_with_feedback.add(feedback.place_uid)
        return web.json_response(
            GetVisitedPlacesResponse(
                places=[
                    Place(
                        uid=p.uid,
                        latitude=p.latitude,
                        longitude=p.longitude,
                        with_feedback=p.uid in places_with_feedback
                    ) for p in user_model.visited_places
                ]
            ).dict(), status=HTTPStatus.OK
        )

        # mock data
        return web.json_response(
            GetVisitedPlacesResponse(
                places=[
                    Place(uid='aaa', latitude=55.733842, longitude=37.588144), 
                    Place(uid='bbb', with_feedback=True, latitude=55.729948, longitude=37.601736),
                ],
            ).dict(), status=HTTPStatus.OK)

    async def post(self, request: AddVisitedPlacesRequest) -> Union[r201[AddVisitedPlacesResponse], r400[CommonError]]:
        await self.dao.add_user_places(
            request.user_email,
            place=PlacesTable(uid=request.place_uid, latitude=request.latitude, longitude=request.longitude)
        )

        return web.json_response(
            AddVisitedPlacesResponse(
                place_uid=request.place_uid
            ).dict(), status=HTTPStatus.CREATED
        )
