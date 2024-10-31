from re import IGNORECASE

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator

from .constants import REGEX_ME, ME_HELP

username_validators = [
    UnicodeUsernameValidator(),
    RegexValidator(
        regex=REGEX_ME,
        flags=IGNORECASE,
        message=ME_HELP
    )
]
