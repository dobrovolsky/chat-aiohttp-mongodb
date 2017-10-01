import json
import uuid

import time
from marshmallow import Schema, fields

from chat.user import user_mongo
from chat.user.Exceptions import UserDoesNotExists


class UserSchema(Schema):
    """Serializer/Deserializer of User instance"""
    _id = fields.String()
    uuid = fields.UUID(required=True)
    email = fields.Email(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    created = fields.Float(required=True)
    is_active = fields.Boolean()


class User:
    """User for manipulation in code"""
    schema = UserSchema()

    def __init__(self, **kwargs) -> None:
        self._id: str = kwargs.get('_id')
        self.uuid: uuid = kwargs.get('uuid', str(uuid.uuid4()))
        self.email: str = kwargs.get('email')
        self.first_name: str = kwargs.get('first_name')
        self.last_name: str = kwargs.get('last_name')
        self.created: float = kwargs.get('created', time.time())
        self.is_active = kwargs.get('is_active', True)

    def __str__(self) -> str:
        return f'id:{self._id}, email:{self.email}'

    def is_valid(self) -> bool:
        """check object validation"""
        self.errors = self._validate()
        return not bool(self.errors)

    def _validate(self) -> dict:
        """validate object with marshmallow"""
        return self.schema.loads(self.schema.dumps(self).data).errors

    def loads(self) -> dict:
        """serialize object to json"""
        return json.loads(self.schema.dumps(self).data)

    def save(self) -> None:
        """save instance to db"""
        if self._id:
            user_mongo.update_user(self)
        else:
            user_mongo.add_user(self)

    @classmethod
    async def get_user(cls, _id) -> 'User':
        """Get user data from db"""
        data = await user_mongo.get_user(_id)
        schema = UserSchema()
        if schema.load(data).data is None:
            raise UserDoesNotExists
        return cls(**schema.load(data).data)

