import aiohttp_jinja2
from aiohttp import web
from aiohttp.web_ws import MsgType


class ChatSocketView(web.View):
    """View for process chat"""

    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        self.request.app['websockets'].append(ws)

        async for msg in ws:
            if msg.tp == MsgType.text:
                self._handler(msg)
                for _ws in self.request.app['websockets']:
                    _ws.send_json('')
            elif msg.tp == MsgType.error:
                print('ws connection closed with exception %s' % ws.exception())
        return ws

    async def _handler(self, msg):
        """Handle ws message"""
        pass


class ChatView(web.View):
    """View for get chat page"""

    @aiohttp_jinja2.template('chat.html')
    async def get(self):
        return {'name': 'Andrew', 'surname': 'Svetlov'}
