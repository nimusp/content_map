from aiohttp import web
from http import HTTPStatus
from aiohttp_pydantic.oas.typing import r200, r201

from api.base_view import BaseView

from api.schema import (
    GetUserFeedbacksResponse, Feedback
)


class UserFeedbacks(BaseView):
    async def get(self, user_email: str) -> r200[GetUserFeedbacksResponse]:
        feedbacks = await self.dao.get_user_feedbacks(user_email=user_email)
        return web.json_response(
            GetUserFeedbacksResponse(
                reviews=[
                    Feedback(
                        user_email=r.user_email,
                        place_uid=r.place_uid,
                        rate=r.rate,
                        feedback_text=r.feedback_text) for r in feedbacks
                ],
            ).dict(),
            status=HTTPStatus.OK)

    async def post(self, feedback: Feedback) -> r201:
        feedback_id = await self.dao.post_user_feedback(feedback=feedback)
        return web.json_response(
            {"feedback_id": feedback_id},
            status=HTTPStatus.OK
        )
