import aiohttp
from http import HTTPStatus
from aiohttp_pydantic import PydanticView

from data.dao import Dao


DB_KEY = 'db_conn'


class AuthErr(Exception):

    def __init__(self, message: str, code: int):
        self.message = message
        self.http_code = code


class BaseView(PydanticView):

    @property
    def dao(self) -> Dao:
        return self.request.app[DB_KEY]

    async def get_email_from_token(self, token: str) -> str:
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'OAuth {token}'}
            query_params = {'format': 'json'}
            async with session.get('https://login.yandex.ru/info', params=query_params, headers=headers) as resp:
                try:
                    resp.raise_for_status()
                except aiohttp.ClientResponseError as ex:
                    raise AuthErr(message=ex.message, code=ex.status)

                resp_body = await resp.json()
                if 'default_email' not in resp_body:
                    raise AuthErr(message='no email in Yandex API response body', code=HTTPStatus.INTERNAL_SERVER_ERROR)

                return resp_body['default_email']
