import asyncio

import jinja2
import aiohttp_jinja2

import uvloop
from aiohttp import web

from chat.config import setup_routes, settings

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
logger = settings.log

if __name__ == '__main__':
    app = web.Application(debug=settings.DEBUG)
    setup_routes(app)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(settings.TEMPLATES_DIR))
    web.run_app(app, host=settings.SITE_HOST, port=settings.SITE_PORT)

