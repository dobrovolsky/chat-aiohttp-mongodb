import logging

import aiohttp_jinja2
from aiohttp import web
from bson import ObjectId
from aiohttp.web_ws import WebSocketResponse

from common.utils import validate_message, multi_dict_to_dict

logger = logging.getLogger('chat')
logger.debug = print

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
                    data, send_to = await self._handle_message(data)
                    for ws in send_to:
                        ws.send_json(data)
                else:
                    return resp
            return resp
        except Exception as e:
            print(e)
        finally:
            await self._handle_disconnection(resp)

    async def _handle_message(self, msg):
        """Handle ws message"""
        action = msg.get('action', '')
        from chat.models import Message
        from chat.models import Room
        if action == 'get_messages':
            return {
                'event': 'get_messages',
                'data': await Message.get_json_messages(msg['room_id']),
                'need_read_count': await self.request.user.get_message_need_count()
            }, [self.request.app['ws_connections'][self.request.user.id]]
        elif action == 'add_message':
            message = await Message.add_message(room_id=msg['room_id'], user=self.request.user, text=msg['text'])
            room = await Room.get_room(_id=ObjectId(msg['room_id']))
            return {
                'event': 'new_message',
                'data': message.loads(),
                'need_read_count': await self.request.user.get_message_need_count()
            }, [self.request.app['ws_connections'][user_id] for user_id in room.members]
        else:
            raise Exception('not allowed action')



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

class CreateChatView(web.View):
    @aiohttp_jinja2.template('start_chat.html')
    async def get(self):
        """show all user's chats"""
        from user.models import User
        context = dict()
        context['user'] = self.request.user
        context['users'] = await User.get_users(**{'_id': {'$ne': ObjectId(self.request.user.id)}})
        return context

    async def post(self):
        """create new chat"""
        from chat.models import Room
        data = multi_dict_to_dict(await self.request.post())
        room = Room(**data)
        if room.is_valid():
            try:
                room.members.append(self.request.user.id)
            except AttributeError:
                room.members = [room.members, self.request.user.id]
            await room.save()
            return web.HTTPFound(f'/chat/{room.id}')
        return web.json_response(data=room.errors, status=400)

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
        context['messages'] = await context['chat'].get_messages()
        return context