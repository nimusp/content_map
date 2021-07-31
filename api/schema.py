from typing import List, Optional
from pydantic import BaseModel, Extra


class Place(BaseModel, extra=Extra.forbid):
    geo_id: int = 0
    with_feedback: bool = False
    latitude: float
    longitude: float

class GetVisitedObjectsResponse(BaseModel, extra=Extra.forbid):
    places: List[Place]
