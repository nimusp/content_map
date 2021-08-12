from typing import Union
from http import HTTPStatus

from aiohttp import web
from aiohttp_pydantic.oas.typing import r200, r201, r404

from api.base_view import BaseView
from api.schema import (
    GetUserFeedbacksResponse,
    Feedback,
    AddUserFeedbackResponse,
    CommonError,
)


class UserFeedbacks(BaseView):
    async def get(
        self, user_email: str
    ) -> Union[r200[AddUserFeedbackResponse], r404[CommonError]]:

        feedbacks = await self.dao.get_user_feedbacks(user_email=user_email)

        if not feedbacks:
            return web.json_response(
                CommonError(error_message="no one feedback for current user").dict(),
                status=HTTPStatus.NOT_FOUND,
            )

        return web.json_response(
            GetUserFeedbacksResponse(
                feedbacks=[
                    Feedback(
                        user_email=f.user_email,
                        place_uid=f.place_uid,
                        rate=f.rate,
                        feedback_text=f.feedback_text,
                    )
                    for f in feedbacks
                ],
            ).dict(),
            status=HTTPStatus.OK,
        )

    async def post(self, feedback: Feedback) -> r201[AddUserFeedbackResponse]:
        feedback_id = await self.dao.post_user_feedback(feedback=feedback)

        return web.json_response(
            AddUserFeedbackResponse(feedback_id=feedback_id).dict(),
            status=HTTPStatus.CREATED,
        )
