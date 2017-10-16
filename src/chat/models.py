import uuid
from typing import List

import time
from marshmallow import Schema, fields

from common.utils import basic_string_validation


class RoomSchema(Schema):
    """Serializer/Deserializer of Room instance"""
    _id = fields.String()
    uuid = fields.UUID(required=True)
    room_name = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=2,
                                                                                        max_length=100))
    members = fields.List(fields.String())
    created = fields.Float(required=True)


class Room:
    """Room for manipulation in code"""
    schema = RoomSchema()

    def __init__(self, **kwargs):
        self._id: str = kwargs.get('_id')
        self.uuid: uuid = kwargs.get('uuid', str(uuid.uuid4()))
        self.room_name: str = kwargs.get('room_name')
        self.members: List[str] = kwargs.get('members')
        self.last_name: str = kwargs.get('last_name')
        self.created: float = kwargs.get('created', time.time())
        for key, value in self.__dict__.copy().items():
            if not value:
                delattr(self, key)

    def __str__(self) -> str:
        return f'id:{self._id}, room name:{self.room_name}'

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

