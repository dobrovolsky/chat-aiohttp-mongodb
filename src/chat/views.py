import aiohttp_jinja2
from aiohttp import web
from aiohttp.web_ws import MsgType
from bson import ObjectId


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


class ChatListView(web.View):
    """View for list of chat"""

    @aiohttp_jinja2.template('chat_list.html')
    async def get(self):
        """show all user's chats"""
        from chat.models import Room
        context = dict()
        context['user'] = self.request.user
        context['chats'] = await Room.get_rooms(self.request.user)
        return context

class ChatView(web.View):
    """View for get chat page"""

    @aiohttp_jinja2.template('chat.html')
    async def get(self):
        """show room page"""
        from chat.models import Room
        chat_id = self.request.match_info['id']
        context = dict()
        context['user'] = self.request.user
        context['chat'] = await Room.get_room(_id=ObjectId(chat_id))
        return context