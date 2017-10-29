from marshmallow import Schema, fields

from common.utils import basic_string_validation


class RoomSchema(Schema):
    """Serializer/Deserializer of Room instance"""
    _id = fields.String()
    room_name = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=2,
                                                                                        max_length=100))
    members = fields.List(fields.String())
    created = fields.Float(required=True)


class MessageSchema(Schema):
    """Serializer/Deserializer of Room instance"""
    _id = fields.String()
    room_id = fields.String()
    from_user_id = fields.String()
    from_user_first_name = fields.String()
    text = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=1,
                                                                                        max_length=10000))
    display_to = fields.List(fields.String())
    need_read = fields.List(fields.String())
    created = fields.Float(required=True)


class AddingMessageValidatorSchema(Schema):
    """Provide validation schema for message"""
    room_id = fields.String(required=True)
    text = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=1, max_length=10000))