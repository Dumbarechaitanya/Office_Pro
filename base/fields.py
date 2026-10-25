"""
EncryptedCharField - a CharField whose value is encrypted (Fernet / AES-128-CBC + HMAC) before it is
written to the database and decrypted when it is read.  Used for secrets the application must be
able to read back (e.g. the SMTP password in ir.mail_server).

Key management
* Set FIELD_ENCRYPTION_KEY in the environment (generate one with
      python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ) -- recommended, because it survives a SECRET_KEY rotation.
* If it is not set, a key is derived from SECRET_KEY.  Rotating SECRET_KEY then makes stored secrets
  unreadable (they read back as empty and must be re-entered).

Backward compatible: values already stored as plaintext are returned as-is and are encrypted the
next time the row is saved (`python manage.py harden_accounts` does this for all mail servers).
"""
import base64
import hashlib
import logging
import os

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)

PREFIX = 'enc1:'


def _fernet():
    key = os.environ.get('FIELD_ENCRYPTION_KEY')
    if key:
        return Fernet(key.encode())
    digest = hashlib.sha256(('officepro-field-encryption:' + settings.SECRET_KEY).encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_value(plain):
    return PREFIX + _fernet().encrypt(plain.encode()).decode()


def decrypt_value(stored):
    return _fernet().decrypt(stored[len(PREFIX):].encode()).decode()


class EncryptedCharField(models.CharField):
    description = 'CharField encrypted at rest'

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value or value.startswith(PREFIX):
            return value
        return encrypt_value(value)

    def from_db_value(self, value, expression, connection):
        if value and value.startswith(PREFIX):
            try:
                return decrypt_value(value)
            except InvalidToken:
                logger.error('Could not decrypt a stored secret (wrong FIELD_ENCRYPTION_KEY / SECRET_KEY?). '
                             'Re-enter the value in the UI.')
                return ''
        return value  # legacy plaintext row
