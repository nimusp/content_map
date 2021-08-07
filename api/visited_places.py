from aiohttp import web
from http import HTTPStatus
from aiohttp_pydantic.oas.typing import r200, r404
from pydantic.typing import Union
from sqlalchemy.exc import NoResultFound

from api.base_view import BaseView

from api.schema import GetVisitedPlacesResponse, GetVisitedPlacesError, Place


class VisitedPlaces(BaseView):

    async def get(self, user_email: str) -> Union[r200[GetVisitedPlacesResponse], r404[GetVisitedPlacesError]]:

        try:
            user_model = await self.dao.get_user_model(user_email)
        except NoResultFound as ex:
            # TODO: log exception
            # TODO: return 404 if len(user_model.visited_places) == 0
            return web.json_response(
                GetVisitedPlacesError(
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
            ).dict(), 
            status=HTTPStatus.OK)