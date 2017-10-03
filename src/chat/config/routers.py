from aiohttp.web import Application

from chat.config import settings
from chat.view import ChatSocketView, ChatView

routers = [
    ('GET', '/chat', ChatView, 'chat'),
    ('GET', '/chat/ws', ChatSocketView, 'chat_ws'),
]


def setup_routes(app: Application):
    """Set up routers"""
    for route in routers:
        app.router.add_route(route[0], route[1], route[2], name=route[3])
    app.router.add_static('/static', settings.STATIC_DIR, name='static')


