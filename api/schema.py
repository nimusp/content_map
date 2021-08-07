from typing import List, Optional
from pydantic import BaseModel, Extra


class Place(BaseModel, extra=Extra.forbid):
    uid: str
    with_feedback: bool = False
    latitude: float
    longitude: float


class GetVisitedPlacesResponse(BaseModel, extra=Extra.forbid):
    places: List[Place]


class GetVisitedPlacesError(BaseModel, extra=Extra.forbid):
    error_message: str
