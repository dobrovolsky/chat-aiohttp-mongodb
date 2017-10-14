from chat.common.validators import BaseValidator
from chat.user.utils import is_email_exists_in_db
from chat.auth.schemas import UserSingUpValidatorSchema, UserSingInValidatorSchema

class UserSingUpValidator(BaseValidator):
    """provide sing up validation"""
    _schema = UserSingUpValidatorSchema()

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.email = kwargs.get('email')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.password1 = kwargs.get('password1')
        self.password2 = kwargs.get('password2')

    async def is_valid(self) -> bool:
        """check object validation"""
        super().is_valid()
        if not self.errors and await is_email_exists_in_db(self.email):
            self.errors.update({'email': 'Email already exists'})
        if not self.errors and self.password1 != self.password2:
            self.errors.update({'non_field_errors': 'password should be the same'})
        return not bool(self.errors)

    def get_data(self):
        if not hasattr(self, 'errors'):
            raise RuntimeError('you must call is_valid() before get data')
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password': self.password1,
        }

class UserSingInValidator(BaseValidator):
    """provide sing in validation"""
    _schema = UserSingInValidatorSchema()

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.email = kwargs.get('email')
        self.password = kwargs.get('password')