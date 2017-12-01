from aiohttp import web

from config import settings
from main import loop, get_app

app = loop.run_until_complete(get_app())
web.run_app(app, host=settings.SITE_HOST, port=settings.SITE_PORT, loop=loop)
