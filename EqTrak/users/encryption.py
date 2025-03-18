from cryptography.fernet import Fernet
from django.conf import settings
import base64

def get_encryption_key():
    """
    Get the encryption key from settings or generate a new one.
    In production, this should always come from environment variables.
    """
    key = getattr(settings, 'ENCRYPTION_KEY', None)
    if not key:
        # For development only - in production, always use a stable key
        # from environment variables to avoid losing access to encrypted data
        key = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode().ljust(32)[:32]).decode()
    return key

def encrypt_value(value):
    """
    Encrypt a string value
    """
    if not value:
        return value
        
    key = get_encryption_key()
    cipher = Fernet(key.encode())
    return cipher.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value):
    """
    Decrypt an encrypted string value
    """
    if not encrypted_value:
        return encrypted_value
        
    key = get_encryption_key()
    cipher = Fernet(key.encode())
    return cipher.decrypt(encrypted_value.encode()).decode()
