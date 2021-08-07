from typing import List, Optional
from pydantic import BaseModel, Extra


class Place(BaseModel, extra=Extra.forbid):
    uid: str
    with_feedback: bool = False
    latitude: float
    longitude: float

class GetVisitedPlacesResponse(BaseModel, extra=Extra.forbid):
    places: List[Place]


class Review(BaseModel, extra=Extra.forbid):
    id: int
    user_email: str
    place_uid: str
    rate: int
    feedback_text: str

class GetUserReviewsResponse(BaseModel, extra=Extra.forbid):
    reviews: List[Review]

