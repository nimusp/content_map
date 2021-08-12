from typing import Optional

from aiohttp import web
from http import HTTPStatus
from aiohttp_pydantic.oas.typing import r200, r201, r400, r404
from pydantic.typing import Union
from sqlalchemy.exc import NoResultFound

from api.base_view import BaseView

from api.schema import (
    GetVisitedPlacesResponse,
    CommonError,
    Place,
    AddVisitedPlacesRequest,
    AddVisitedPlacesResponse,
    UserContext,
    PlaceState,
    FeedbackSmall,
)
from data.schema import UsersTable, PlacesTable


class VisitedPlaces(BaseView):

    async def get(
            self, user_email: str,
            latitude: Optional[float] = 0, longitude: Optional[float] = 0,
            zoom: Optional[float] = 0,
            state: Optional[UserContext] = UserContext.default,
    ) -> Union[r200[GetVisitedPlacesResponse], r404[CommonError]]:
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

        feedbacks_by_uids = {}
        for feedback in user_model.feedbacks:
            feedbacks_by_uids[feedback.place_uid] = FeedbackSmall(rate=feedback.rate, text=feedback.feedback_text)

        user_places = [
                    Place(
                        uid=p.uid,
                        id=p.id,
                        latitude=p.latitude,
                        longitude=p.longitude,
                        feedback=feedbacks_by_uids.get(p.uid, None),
                    ) for p in user_model.visited_places
                ]

        # TODO: find closest for passed lat/lon + zoom
        if state == UserContext.default:
            user_places = user_places[:1]
            user_places[0].state = PlaceState.full

        return web.json_response(GetVisitedPlacesResponse(places=user_places).dict(), status=HTTPStatus.OK)

    async def post(self, request: AddVisitedPlacesRequest) -> Union[r201[AddVisitedPlacesResponse], r400[CommonError]]:
        await self.dao.add_user_places(
            request.user_email,
            place=PlacesTable(
                uid=request.place_uid,
                id=request.place_id,
                latitude=request.latitude,
                longitude=request.longitude,
            ),
        )

        return web.json_response(
            AddVisitedPlacesResponse(
                place_uid=request.place_uid
            ).dict(), status=HTTPStatus.CREATED
        )
