from aiohttp import WSMsgType
from marshmallow import ValidationError


def basic_string_validation(value, min_length=None, max_length=None, blank=False):
    """Provide basic validation for string"""
    if not isinstance(value, str):
        raise ValidationError('should be a string')
    if min_length and len(value) < min_length:
        raise ValidationError(f'string should be longer than {min_length}')
    if max_length and len(value) > max_length:
        raise ValidationError(f'string should be shorter than {max_length}')
    if not blank and not value:
        raise ValidationError(f'string should not be blank')


def validate_message(message):
    if message.type == WSMsgType.TEXT:
        data = message.json()
        return data, True
    else:
        return None, False