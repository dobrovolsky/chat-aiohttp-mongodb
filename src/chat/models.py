import uuid

import base64

from typing import List, Dict

from chat.exceptions import RoomValidationError, RoomDoesNotExists, MessageValidationError
from chat.schemas import RoomSchema, MessageSchema
from common.models import BaseModel
from common.utils import bind_media_url
from config import MEDIA_DIR
from user.utils import get_room_collection, get_message_collection

room_collection = get_room_collection()
message_collection = get_message_collection()


class Room(BaseModel):
    """Room for manipulation in code"""
    schema = RoomSchema()
    fields = (
        ('_id', None),
        ('room_name', None),
        ('members', []),
        ('created', BaseModel.default_current_time),
        ('is_active', True),
    )

    def __str__(self) -> str:
        instance_id = None
        if hasattr(self, "_id"):
            instance_id = self.id
        return f'id:{instance_id}, room name:{self.room_name}'

    async def save(self) -> None:
        """save instance to db"""
        if not hasattr(self, 'errors'):
            raise RuntimeError('you must call is_valid() before save instance')
        if self.errors:
            raise RoomValidationError(self.errors)
        if hasattr(self, '_id'):
            data = self.loads()
            room_id = data.pop('_id')
            await room_collection.replace_one({'_id': room_id}, data)
        else:
            result = await room_collection.insert_one(self.loads())
            self._id = result.inserted_id

    @classmethod
    async def get_rooms(cls, user) -> List['Room']:
        rooms = []
        schema = RoomSchema()
        async for document in room_collection.find({'members': user.id}):
            document['_id'] = str(document['_id'])
            rooms.append(cls(**schema.load(document).data))
        return rooms

    @classmethod
    async def get_room(cls, **filters) -> 'Room':
        """Get data from db"""
        data = await room_collection.find_one(filters)
        schema = RoomSchema()
        if schema.load(data).data is None:
            raise RoomDoesNotExists
        data['_id'] = str(data['_id'])
        return cls(**schema.load(data).data)

    async def get_messages(self) -> List['Message']:
        return await Message.get_messages(self._id)

    @classmethod
    async def get_json_rooms(cls, user) -> List[Dict]:
        data = await cls.get_rooms(user)
        result = []
        for room in data:
            result.append(room.loads())
        return result

    @staticmethod
    async def get_last_message(room_id) -> 'Message':
        schema = MessageSchema()
        document = await message_collection.find_one({'room_id': room_id}, sort=[('created', -1)])
        instance = Message(**schema.load(document).data)
        return instance


class Message(BaseModel):
    """Message for manipulation in code"""
    schema = MessageSchema()
    fields = (
        ('_id', None),
        ('room_id', None),
        ('from_user_id', None),
        ('from_user_first_name', None),
        ('text', None),
        ('file', None),
        ('display_to', []),
        ('need_read', []),
        ('created', BaseModel.default_current_time),
    )

    def bind_media_url(self) -> dict:
        if hasattr(self, 'file') and self.file:
            self.file = bind_media_url(self.file)
        return super().loads()

    async def save(self) -> None:
        """save instance to db"""
        if not hasattr(self, 'errors'):
            raise RuntimeError('you must call is_valid() before save instance')
        if self.errors:
            raise MessageValidationError(self.errors)
        if hasattr(self, '_id'):
            data = self.loads()
            message_id = data.pop('_id')
            await message_collection.replace_one({'_id': message_id}, data)
        else:
            result = await message_collection.insert_one(self.loads())
            self._id = result.inserted_id

    @classmethod
    async def add_message(cls, room, user, text):
        need_read = room.members[:]
        need_read.remove(user.id)
        data = {
            'room_id': room.id,
            'from_user_id': user.id,
            'from_user_first_name': user.first_name,
            'display_to': room.members[:],
            'need_read': need_read,
            'text': text,
        }
        message = cls(**data)
        message.is_valid()
        await message.save()
        message.bind_media_url()
        return message

    @classmethod
    async def get_messages(cls, room_id) -> List['Message']:
        messages = []
        schema = MessageSchema()
        async for document in message_collection.find({'room_id': room_id}):
            document['_id'] = str(document['_id'])
            instance = cls(**schema.load(document).data)
            instance.bind_media_url()
            messages.append(instance)
        return messages

    @classmethod
    async def get_json_messages(cls, room_id) -> List['Message']:
        data = await cls.get_messages(room_id)
        result = []
        for message in data:
            result.append(message.loads())
        return result

    @staticmethod
    async def get_message_read_count(user_id, room_id=None) -> int:
        result = 0
        query_filter = {'need_read': user_id}
        if room_id:
            query_filter = {'$and': [query_filter, {'room_id': room_id}]}
        query = message_collection.aggregate([
                {'$match': query_filter},
                {'$group': {'_id': None, 'count': {'$sum': 1}}}
            ]
        )
        async for document in query:
            result = document['count']
        return result

    @classmethod
    async def add_file(cls, room, user, file_data):
        decoded_file = base64.b64decode(file_data['content'])
        name = uuid.uuid4().hex[:8] + '.' + file_data['file_name'].split('.')[-1]
        file_path = MEDIA_DIR + '/' + name
        with open(file_path, 'wb') as f:
            f.write(decoded_file)
        data = {
            'room_id': room.id,
            'from_user_id': user.id,
            'from_user_first_name': user.first_name,
            'display_to': room.members[:],
            'need_read': room.members[:].remove(user.id) or [],
            'file': name,
            'text': file_data['file_name']
        }
        message = cls(**data)
        message.is_valid()
        await message.save()
        message.bind_media_url()
        return message
