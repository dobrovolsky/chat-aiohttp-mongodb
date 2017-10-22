from marshmallow import Schema, fields

from common.models import BaseModel
from user.Exceptions import UserDoesNotExists, UserValidationError

from common.utils import basic_string_validation
from user.utils import get_hash, get_user_collection

collection = get_user_collection()


class UserSchema(Schema):
    """Serializer/Deserializer of User instance"""
    _id = fields.String()
    email = fields.Email(required=True)
    first_name = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=2,
                                                                                         max_length=100))
    last_name = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=2,
                                                                                        max_length=100))
    created = fields.Float(required=True)
    is_active = fields.Boolean()
    password = fields.String(required=True)


class User(BaseModel):
    """User for manipulation in code"""
    schema = UserSchema()
    fields = (
        ('_id', None),
        ('email', None),
        ('first_name', None),
        ('last_name', None),
        ('created', BaseModel.default_current_time),
        ('is_active', True),
        ('password', None),
    )

    def __str__(self) -> str:
        return f'id:{self._id}, email:{self.email}'

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
            self._id = result.inserted_id

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