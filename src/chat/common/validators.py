from marshmallow import Schema


class BaseValidator:
    """base validator"""
    def __init__(self):
        self.schema = self.get_schema()

    def get_schema(self):
        """get marshmallow schema"""
        if not hasattr(self, '_schema'):
            raise NotImplemented('Validator should implement self.schema attr')
        if not isinstance(self._schema, Schema):
            raise RuntimeError('self.schema should be Schema instance')
        return self._schema

    def is_valid(self) -> bool:
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
