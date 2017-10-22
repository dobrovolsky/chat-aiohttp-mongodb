import logging

import aiohttp_jinja2
from aiohttp import web
from bson import ObjectId
from aiohttp.web_ws import WebSocketResponse

from common.utils import validate_message


logger = logging.getLogger('chat')

class ChatSocketView(web.View):
    """View for process chat"""

    async def get(self):
        resp, ok = await self._handle_connection()
        if not ok:
            return resp or web.Response()
        try:
            async for msg in resp:
                logger.debug(f'new message {msg}')
                data, ok = validate_message(msg)
                if ok:
                    await self._handle_message(data)
                    for user, ws in self.request.app['ws_connections'].items():
                        await ws.send_str(msg.data)
                else:
                    return resp
            return resp
        finally:
            await self._handle_disconnection(resp)

    async def _handle_message(self, msg):
        """Handle ws message"""
        from chat.models import Message, Room
        room = await Room.get_room(_id=ObjectId(msg['room_id']))
        display_to = room.members[:]
        need_read = display_to[:]
        need_read.remove(self.request.user.id)
        msg.update({
            'display_to': display_to,
            'need_read': need_read
        })
        message = Message(**msg)
        message.is_valid()
        await message.save()

    async def _handle_disconnection(self, resp):
        del self.request.app['ws_connections'][self.request.user.id]
        logger.debug(f'{self.request.user} has been disconnected')

    async def _handle_connection(self):
        resp = WebSocketResponse()
        ok, protocol = resp.can_prepare(self.request)
        if not ok:
            return None, ok
        await resp.prepare(self.request)
        self.request.app['ws_connections'][self.request.user.id] = resp
        logger.debug(f'{self.request.user} has been connected')
        return resp, ok


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