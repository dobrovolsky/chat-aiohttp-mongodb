import json
from typing import List

import time
from marshmallow import Schema, fields

from chat.Exceptions import RoomValidationError, RoomDoesNotExists
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


class Room:
    """Room for manipulation in code"""
    schema = RoomSchema()

    def __init__(self, **kwargs):
        self._id: str = kwargs.get('_id')
        self.room_name: str = kwargs.get('room_name')
        self.members: List[str] = kwargs.get('members')
        self.created: float = kwargs.get('created', time.time())
        for key, value in self.__dict__.copy().items():
            if not value:
                delattr(self, key)

    def __str__(self) -> str:
        return f'id:{self._id}, room name:{self.room_name}'

    @property
    def id(self):
        return self._id

    async def is_valid(self) -> bool:
        """check object validation"""
        self.errors = self._validate()
        return not bool(self.errors)

    def _validate(self) -> dict:
        """validate object with marshmallow"""
        user = self.schema.dumps(self)
        errors = self.schema.loads(user.data).errors
        if user.errors:
            errors.update(user.errors)
        return errors

    def loads(self) -> dict:
        """serialize object to json"""
        return json.loads(self.schema.dumps(self).data)

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

class Message:
    """Room for manipulation in code"""
    schema = RoomSchema()

    def __init__(self, **kwargs):
        self._id: str = kwargs.get('_id')
        self.room_id: str = kwargs.get('room_id')
        self.display_to: List[str] = kwargs.get('display_to')
        self.read_by: List[str] = kwargs.get('read_by')
        self.created: float = kwargs.get('created', time.time())
        for key, value in self.__dict__.copy().items():
            if not value:
                delattr(self, key)

    @property
    def id(self):
        return self._id