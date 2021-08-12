from typing import List, Optional
from pydantic import (
    BaseModel, Extra, validator, EmailStr,
    conint, confloat
)


class Place(BaseModel, extra=Extra.forbid):
    uid: str
    with_feedback: bool = False
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)


class GetVisitedPlacesResponse(BaseModel, extra=Extra.forbid):
    places: List[Place]


class CommonError(BaseModel, extra=Extra.forbid):
    error_message: str


class AddVisitedPlacesRequest(BaseModel, extra=Extra.forbid):
    user_email: str
    place_uid: str
    latitude: float
    longitude: float


class AddVisitedPlacesResponse(BaseModel, extra=Extra.forbid):
    place_uid: str


class Feedback(BaseModel, extra=Extra.forbid):
    user_email: EmailStr
    place_uid: str
    rate: conint(ge=0, le=5)
    feedback_text: str


class GetUserFeedbacksResponse(BaseModel, extra=Extra.forbid):
    feedbacks: List[Feedback]


class AddUserFeedbackResponse(BaseModel, extra=Extra.forbid):
    feedback_id: int
