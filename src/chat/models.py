from typing import List

from marshmallow import Schema, fields

from chat.Exceptions import RoomValidationError, RoomDoesNotExists
from common.models import BaseModel
from common.utils import basic_string_validation
from user.utils import get_room_collection

collection = get_room_collection()

class RoomSchema(Schema):
    """Serializer/Deserializer of Room instance"""
    _id = fields.String()
    room_name = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=2,
                                                                                        max_length=100))
    members = fields.List(fields.String())
    created = fields.Float(required=True)


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
            user_id = data.pop('_id')
            await collection.replace_one({'_id': user_id}, data)
        else:
            result = await collection.insert_one(self.loads())
            self._id = result.inserted_id

    @classmethod
    async def get_rooms(cls, user) -> List['Room']:
        rooms = []
        schema = RoomSchema()
        async for document in collection.find({'members': user._id}):
            document['_id'] = str(document['_id'])
            rooms.append(cls(**schema.load(document).data))
        return rooms

    @classmethod
    async def get_room(cls, **filters) -> 'Room':
        """Get user data from db"""
        print(filters)
        data = await collection.find_one(filters)
        schema = RoomSchema()
        if schema.load(data).data is None:
            raise RoomDoesNotExists
        data['_id'] = str(data['_id'])
        return cls(**schema.load(data).data)


class MessageSchema(Schema):
    """Serializer/Deserializer of Room instance"""
    _id = fields.String()
    room_id = fields.String()
    uuid = fields.UUID(required=True)
    display_to = fields.List(fields.String())
    read_by = fields.List(fields.String())
    created = fields.Float(required=True)


class Message(BaseModel):
    """Message for manipulation in code"""
    schema = MessageSchema()
    fields = (
        ('_id', None),
        ('room_id', None),
        ('display_to', []),
        ('read_by', []),
        ('created', BaseModel.default_current_time),
    )

