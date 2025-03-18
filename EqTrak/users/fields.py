from django.db import models
from django.utils.functional import cached_property
from . import encryption

class EncryptedCharField(models.CharField):
    """
    Custom field that stores values encrypted in the database.
    Decrypts values when accessed.
    """
    
    description = "Encrypted CharField"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return encryption.decrypt_value(value)
    
    def to_python(self, value):
        if value is None:
            return value
        # If value is already decrypted, don't decrypt again
        # This can happen during form validation
        try:
            return encryption.decrypt_value(value)
        except:
            # Value was likely already decrypted
            return value
    
    def get_prep_value(self, value):
        if value is None:
            return value
        # Make sure we don't double-encrypt
        try:
            # Try to decrypt to see if it's already encrypted
            encryption.decrypt_value(value)
            # If it worked, it was already encrypted
            return value
        except:
            # If decryption fails, it wasn't encrypted yet
            return encryption.encrypt_value(value)
