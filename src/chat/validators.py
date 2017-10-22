from chat.schemas import AddingMessageValidatorSchema
from common.validators import BaseValidator


class AddingMessageValidator(BaseValidator):
    """provide adding message validation"""
    _schema = AddingMessageValidatorSchema()

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.room_id = kwargs.get('room_id')
        self.text = kwargs.get('text')