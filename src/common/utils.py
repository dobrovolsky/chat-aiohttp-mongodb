from aiohttp import WSMsgType
from marshmallow import ValidationError

from config import settings


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


def multi_dict_to_dict(data):
    data2 = dict()
    for key, value in data.items():
        if key in data2:
            if isinstance(data2[key], list):
                data2[key].append(value)
            else:
                tmp = data2[key]
                data2[key] = [tmp, value]
        else:
            data2[key] = value
    return data2


def bind_media_url(file_name):
    connection_type = 'http://'
    if settings.IS_SECURE:
        connection_type = 'https://'
    return f'{connection_type}{settings.SITE_HOST}:{settings.SITE_PORT}{settings.MEDIA_URL}{file_name}'
