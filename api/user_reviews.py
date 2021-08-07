from aiohttp import web
from http import HTTPStatus
from aiohttp_pydantic.oas.typing import r200, r201

from api.base_view import BaseView

from api.schema import (
    GetUserReviewsResponse, Review
)


class UserReviews(BaseView):
    async def get(self, user_email: str) -> r200[GetUserReviewsResponse]:
        reviews = await self.dao.get_user_reviews(user_email=user_email)
        return web.json_response(
            GetUserReviewsResponse(
                reviews=[
                    Review(
                        id=r.id,
                        user_email=r.user_email,
                        place_uid=r.place_uid,
                        rate=r.rate,
                        feedback_text=r.feedback_text) for r in reviews
                ],
            ).dict(),
            status=HTTPStatus.OK)

    async def post(self, review: Review) -> r201:
        review_id = await self.dao.post_user_review(review=review)
        return web.json_response(
            {"review_id": review_id},
            status=HTTPStatus.OK
        )
