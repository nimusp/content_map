from typing import List, Optional
from pydantic import BaseModel, Extra


class Place(BaseModel, extra=Extra.forbid):
    uid: str
    with_feedback: bool = False
    latitude: float
    longitude: float

class GetVisitedPlacesResponse(BaseModel, extra=Extra.forbid):
    places: List[Place]


class Feedback(BaseModel, extra=Extra.forbid):
    user_email: str
    place_uid: str
    rate: int
    feedback_text: str

class GetUserFeedbacksResponse(BaseModel, extra=Extra.forbid):
    feedbacks: List[Feedback]

class AddUserFeedbackResponse(BaseModel, extra=Extra.forbid):
    feedback_id: int


class CommonError(BaseModel, extra=Extra.forbid):
    message: str
