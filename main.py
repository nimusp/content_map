from aiohttp import web
from aiohttp_pydantic import oas

from api.base_view import DB_KEY

from api.visited_places import VisitedPlaces
from api.user_feedbacks import UserFeedbacks

from data.schema import get_db_conn_sessionmaker

from data.dao import Dao


app = web.Application()
app.add_routes([
    web.get('/visited_places', VisitedPlaces),
    web.post('/visited_places', VisitedPlaces),
    web.get('/user_feedbacks', UserFeedbacks),
    web.post('/user_feedback', UserFeedbacks),
])


async def on_startup(app: web.Application):
    app[DB_KEY] = Dao(get_db_conn_sessionmaker())

app.on_startup.append(on_startup)
oas.setup(app, url_prefix="/docs")

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
