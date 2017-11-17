from aiohttp.web import Application
from chat.views import ChatSocketView, ChatListView, ChatView, CreateChatView

from config import settings


def setup_routes(app: Application):
    """Set up routers"""
    from auth.views import SignUpView, SignInView
    routers = [
        ('GET', '/chat-list', ChatListView, 'chat_list'),
        ('GET', '/chat/{id}', ChatView, 'chat'),
        ('*', '/start-chat', CreateChatView, 'start_chat'),
        ('GET', '/ws/chat', ChatSocketView, 'chat_ws'),
        ('*', '/signup', SignUpView, 'signup'),
        ('*',   '/signin',  SignInView, 'signin'),
        # ('*',   '/signout', SignOut, 'signout'),
    ]
    for route in routers:
        app.router.add_route(route[0], route[1], route[2], name=route[3])
    app.router.add_static('/static', settings.STATIC_DIR, name='static')
    app.router.add_static(settings.MEDIA_URL, settings.MEDIA_DIR, name='media')
    app['static_root_url'] = '/static'


