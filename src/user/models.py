import json
import time
import uuid

from user.Exceptions import UserDoesNotExists, UserValidationError
from marshmallow import Schema, fields

from user.utils import get_hash, get_message_collection, basic_string_validation

collection = get_message_collection()


class UserSchema(Schema):
    """Serializer/Deserializer of User instance"""
    _id = fields.String()
    uuid = fields.UUID(required=True)
    email = fields.Email(required=True)
    first_name = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=2,
                                                                                         max_length=100))
    last_name = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=2,
                                                                                        max_length=100))
    created = fields.Float(required=True)
    is_active = fields.Boolean()
    password = fields.String(required=True)


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
        self.password = kwargs.get('password')
        for key, value in self.__dict__.copy().items():
            if not value:
                delattr(self, key)

    def __str__(self) -> str:
        return f'id:{self._id}, email:{self.email}'

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
            raise UserValidationError(self.errors)
        if hasattr(self, '_id'):
            data = self.loads()
            user_id = data.pop('_id')
            await collection.replace_one({'_id': user_id}, data)
        else:
            self.set_password(self.password)
            result = await collection.insert_one(self.loads())
            self.id = result.inserted_id

    @classmethod
    async def get_user(cls, **filters) -> 'User':
        """Get user data from db"""
        data = await collection.find_one(filters)
        schema = UserSchema()
        if schema.load(data).data is None:
            raise UserDoesNotExists
        data['_id'] = str(data['_id'])
        return cls(**schema.load(data).data)

    def set_password(self, raw_password):
        """Set password for user"""
        self.password = get_hash(raw_password)

    def check_password(self, raw_password):
        """check password for user"""
        return self.password == get_hash(raw_password)
