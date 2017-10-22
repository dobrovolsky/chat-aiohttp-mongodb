import json
import time

from marshmallow import Schema


class BaseModel:

    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'fields'):
            raise NotImplementedError('you should provide fields attr with field name Example : ("name", None), '
                                      'name is field name and None is default value')
        for field in self.fields:
            setattr(self, field[0], kwargs.get(field[0], field[1]))
        for key, value in self.__dict__.copy().items():
            if value is None:
                delattr(self, key)

    @property
    def id(self):
        return self._id

    def is_valid(self) -> bool:
        """check object validation"""
        self.errors = self._validate()
        return not bool(self.errors)

    def _validate(self) -> dict:
        """validate object with marshmallow"""
        if not hasattr(self, 'schema') and not isinstance(self.schema, Schema):
            raise NotImplementedError('class should have schema instance of `Schema`')
        user = self.schema.dumps(self)
        errors = self.schema.loads(user.data).errors
        if user.errors:
            errors.update(user.errors)
        return errors

    def loads(self) -> dict:
        """serialize object to json"""
        return json.loads(self.schema.dumps(self).data)

    @staticmethod
    def default_current_time():
        return time.time()