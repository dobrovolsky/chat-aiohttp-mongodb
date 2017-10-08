from aiohttp.web import Application

from chat.config import settings
from chat.views import ChatSocketView, ChatView


def setup_routes(app: Application):
    """Set up routers"""
    from chat.auth.views import SignUp
    routers = [
        ('GET', '/chat', ChatView, 'chat'),
        ('GET', '/chat/ws', ChatSocketView, 'chat_ws'),
        ('*', '/signup', SignUp, 'signup'),
        # ('*',   '/login',   Login, 'login'),
        # ('*',   '/signin',  SignIn, 'signin'),
        # ('*',   '/signout', SignOut, 'signout'),
    ]
    for route in routers:
        app.router.add_route(route[0], route[1], route[2], name=route[3])
    app.router.add_static('/static', settings.STATIC_DIR, name='static')


