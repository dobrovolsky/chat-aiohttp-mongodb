from marshmallow import Schema, fields

from chat.user.utils import basic_string_validation


class UserSingUpValidatorSchema(Schema):
    """Provide validation schema for SingUp"""
    email = fields.Email(required=True)
    first_name = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=2,
                                                                                         max_length=50))
    last_name = fields.String(required=True,
                              validate=lambda n: basic_string_validation(n, min_length=2, max_length=50))
    password1 = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=6, max_length=50))
    password2 = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=6, max_length=50))


class UserSingInValidatorSchema(Schema):
    """Provide validation schema for SingIn"""
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=lambda n: basic_string_validation(n, min_length=6, max_length=50))