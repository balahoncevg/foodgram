import random
import string

from django.core.mail import send_mail

from .constants import FROM_EMAIL, MESSAGE, SUBJECT


def send_confirmation_code(email, confirmation_code) -> None:
    send_mail(
        subject=SUBJECT,
        message=MESSAGE.format(confirmation_code),
        from_email=FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )


def generate_short_link():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))
