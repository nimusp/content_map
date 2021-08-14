from typing import List, Optional, Union
from dataclasses import dataclass
from pydantic import (
    BaseModel, EmailStr,
    conint, confloat
)
from enum import Enum, IntEnum


@dataclass
class ScreenResolution:
    width: Union[int, float]
    height: Union[int, float]


class UserContext(str, Enum):
    default = 'DEFAULT'
    ugc = 'UGC'


class PlaceState(IntEnum):
    full = 1
    smallest = 5


class FeedbackSmall(BaseModel):
    rate: int = 0
    text: str = ''


class Place(BaseModel):
    uid: str
    id: int = 0
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)
    state: PlaceState = PlaceState.smallest


class GetVisitedPlacesResponse(BaseModel):
    places: List[Place]


class CommonError(BaseModel):
    error_message: str


class AddVisitedPlacesRequest(BaseModel):
    user_email: Optional[str]
    place_uid: str
    place_id: int = 0
    latitude: float
    longitude: float


class AddVisitedPlacesResponse(BaseModel):
    place_uid: str


class Feedback(BaseModel):
    user_email: Optional[EmailStr]
    place_uid: str
    rate: conint(ge=0, le=5)
    feedback_text: str


class GetUserFeedbacksResponse(BaseModel):
    feedbacks: List[Feedback]


class AddUserFeedbackResponse(BaseModel):
    feedback_id: int
