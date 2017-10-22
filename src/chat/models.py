from typing import List

from chat.Exceptions import RoomValidationError, RoomDoesNotExists, MessageValidationError
from chat.schemas import RoomSchema, MessageSchema
from common.models import BaseModel
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
        ('password', None),
    )

    def __str__(self) -> str:
        return f'id:{self._id}, room name:{self.room_name}'

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
        async for document in room_collection.find({'members': user._id}):
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


class Message(BaseModel):
    """Message for manipulation in code"""
    schema = MessageSchema()
    fields = (
        ('_id', None),
        ('room_id', None),
        ('text', None),
        ('display_to', []),
        ('need_read', []),
        ('created', BaseModel.default_current_time),
    )

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

