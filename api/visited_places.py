from typing import Optional, Union

from aiohttp import web
from http import HTTPStatus
from aiohttp_pydantic.oas.typing import r200, r201, r400, r404
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
    ScreenResolution,
)
from pydantic import (
    confloat
)
from data.schema import UsersTable, PlacesTable
from utils.emulator_specifications import EMULATOR_SCREEN


class VisitedPlaces(BaseView):
    # FIXME: without feedback data

    async def get(
            self, user_email: str,
            latitude: float,
            longitude: float,
            zoom: float,
            device_width: Optional[Union[int, float]] = EMULATOR_SCREEN.width,
            device_height: Optional[Union[int, float]] = EMULATOR_SCREEN.height,
            state: Optional[UserContext] = UserContext.default,
    ) -> Union[r200[GetVisitedPlacesResponse], r404[CommonError]]:
        if zoom < 2.0 or zoom > 21.0:
            return web.json_response(
                CommonError(
                    error_message=f'invalid zoom, must be 2.0 <= zoom <= 21.0; {zoom}'
                ).dict(), status=HTTPStatus.NOT_FOUND
            )
        if zoom > 17.0:
            zoom = 17.0


        device = ScreenResolution(device_width, device_height)
        user_places = await self.dao.get_visited_places(
            email=user_email,
            latitude=latitude, longitude=longitude, zoom=zoom, device=device
        )
        if state == UserContext.default:
            # Берем первый элемент, т.к. запрос к БД
            # вернул отсортированный по дистанции список
            place = user_places.first()
            if place:
                uid, id_, lon, lat = place
                closest_place = Place(
                    uid=uid,
                    id=id_,
                    latitude=lat,
                    longitude=lon,
                    state=PlaceState.full
                )
                print(closest_place)
                return web.json_response(
                    GetVisitedPlacesResponse(places=[closest_place]).dict(),
                    status=HTTPStatus.OK
                )
            else:
                return web.json_response(
                    CommonError(
                        error_message=f'no data for user with email {user_email}'
                    ).dict(), status=HTTPStatus.NOT_FOUND
                )

        places = [
            Place(
                uid=uid,
                id=id_,
                latitude=lat,
                longitude=lon,
                state=PlaceState.smallest
            ) for uid, id_, lat, lon in user_places.all()
        ]
        # Изменяем PlaceState на full для ближайшей точки
        if places:
            places[0].state = PlaceState.full
        return web.json_response(
            GetVisitedPlacesResponse(places=places).dict(),
            status=HTTPStatus.OK
        )

    async def post(
            self, request: AddVisitedPlacesRequest
    ) -> Union[r201[AddVisitedPlacesResponse], r400[CommonError]]:

        coordinates = f'POINT({request.longitude} {request.latitude})'
        await self.dao.add_user_places(
            request.user_email,
            place=PlacesTable(
                uid=request.place_uid,
                id=request.place_id,
                coordinates=coordinates
            ),
        )

        return web.json_response(
            AddVisitedPlacesResponse(
                place_uid=request.place_uid
            ).dict(), status=HTTPStatus.CREATED
        )
