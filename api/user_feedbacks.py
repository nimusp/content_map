from typing import Union, Optional
from http import HTTPStatus

from aiohttp import web
from aiohttp_pydantic.oas.typing import r200, r201, r400, r401, r404

from api.base_view import BaseView, AuthErr
from api.schema import (
    GetUserFeedbacksResponse,
    Feedback,
    AddUserFeedbackResponse,
    CommonError,
)


class UserFeedbacks(BaseView):
    async def get(
            self, user_email: Optional[str],
            *, token: Optional[str] = '',
    ) -> Union[r200[GetUserFeedbacksResponse], r400[CommonError], r401[CommonError], r404[CommonError]]:
        # TODO: delete me after auth token use
        if not user_email and not token:
            return web.json_response(
                CommonError(error_message='token or email must be not empty').dict(),
                status=HTTPStatus.BAD_REQUEST,
            )

        if token:
            try:
                user_email = await self.get_email_from_token(token)
            except AuthErr as ex:
                return web.json_response(CommonError(error_message=ex.message).dict(), status=ex.http_code)

        feedbacks = await self.dao.get_user_feedbacks(user_email=user_email)

        # TODO: set token NOT optional later
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

    async def post(
            self, feedback: Feedback,
            *, token: Optional[str] = '',
    ) -> Union[r201[AddUserFeedbackResponse], r400[CommonError], r401[CommonError]]:
        # TODO: delete me after auth token use
        if not feedback.user_email and not token:
            return web.json_response(
                CommonError(error_message='token or email must be not empty').dict(),
                status=HTTPStatus.BAD_REQUEST,
            )

        # TODO: set token NOT optional later
        if token:
            try:
                feedback.user_email = await self.get_email_from_token(token)
            except AuthErr as ex:
                return web.json_response(CommonError(error_message=ex.message).dict(), status=ex.http_code)

        feedback_id = await self.dao.post_user_feedback(feedback=feedback)

        return web.json_response(
            AddUserFeedbackResponse(feedback_id=feedback_id).dict(),
            status=HTTPStatus.CREATED,
        )
