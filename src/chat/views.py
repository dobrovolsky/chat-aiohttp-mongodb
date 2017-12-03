import logging

import aiohttp_jinja2
from aiohttp import web
from bson import ObjectId
from aiohttp.web_ws import WebSocketResponse

from common.utils import validate_message, multi_dict_to_dict
from common.view_mixins import LoginRequiredMixin

logger = logging.getLogger('chat')
logger.debug = print


class ChatSocketView(LoginRequiredMixin, web.View):
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
            logger.debug(e)
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
            room = await Room.get_room(_id=ObjectId(msg['room_id']))
            message = await Message.add_message(room=room, user=self.request.user, text=msg['text'])
            data = {
                'event': 'new_message',
                'data': message.loads(),
                'need_read_count': await self.request.user.get_message_need_count()
            }
            return data, (self.request.app['ws_connections'].get(user_id)
                for user_id in room.members if self.request.app['ws_connections'].get(user_id))
        elif action == 'get_rooms':
            rooms = await Room.get_json_rooms(user=self.request.user)
            for r in rooms:
                last_message = await Room.get_last_message(r['_id'])
                count_unread = await Message.get_message_read_count(user_id=self.request.user.id, room_id=r['_id'])
                r['last_message'] = last_message.loads()
                r['read_count'] = count_unread
            return {
               'event': 'get_rooms',
               'data': rooms,
               'need_read_count': await self.request.user.get_message_need_count()
            }, [self.request.app['ws_connections'][self.request.user.id]]
        elif action == 'add_file':
            room = await Room.get_room(_id=ObjectId(msg['room_id']))
            message = await Message.add_file(room=room, user=self.request.user, file_data=msg['file_data'])
            data = {
                'event': 'new_message',
                'data': message.loads(),
                'need_read_count': await self.request.user.get_message_need_count()
            }
            return data, (self.request.app['ws_connections'].get(user_id)
                for user_id in room.members if self.request.app['ws_connections'].get(user_id))

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


class ChatListView(LoginRequiredMixin, web.View):
    """View for list of chat"""

    @aiohttp_jinja2.template('chat_list.html')
    async def get(self):
        """show all user's chats"""
        from chat.models import Room
        context = dict()
        context['user'] = self.request.user
        context['chats'] = await Room.get_rooms(self.request.user)
        context['request'] = self.request
        return context


class CreateChatView(LoginRequiredMixin, web.View):
    @aiohttp_jinja2.template('start_chat.html')
    async def get(self):
        """show all user's chats"""
        from user.models import User
        context = dict()
        context['user'] = self.request.user
        context['users'] = await User.get_users(**{'_id': {'$ne': ObjectId(self.request.user.id)}})
        context['request'] = self.request
        return context

    async def post(self):
        """create new chat"""
        from chat.models import Room, Message
        data = multi_dict_to_dict(await self.request.post())
        room = Room(**data)
        if room.is_valid():
            try:
                room.members.append(self.request.user.id)
            except AttributeError:
                room.members = [room.members, self.request.user.id]
            await room.save()
            await Message.add_message(room=room, user=self.request.user, text='crate new room')
            return web.HTTPFound(f'/chat/{room.id}')
        return web.json_response(data=room.errors, status=400)


class ChatView(LoginRequiredMixin, web.View):
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
        context['request'] = self.request
        return context
