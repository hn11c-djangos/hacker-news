import re
from django.core.exceptions import ValidationError

def validate_username(value):
    if not re.match(r'^[a-zA-Z0-9_-]{2,15}$', value):
        raise ValidationError(
            'Usernames can only contain letters, digits, dashes and underscores, and should be between 2 and 15 characters long. Please choose another.'
        )