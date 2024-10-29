import random
import string
import tempfile

from recipes.models import IngredientRecipe

'''from django.core.mail import send_mail

from .constants import FROM_EMAIL, MESSAGE, SUBJECT


def send_confirmation_code(email, confirmation_code) -> None:
    send_mail(
        subject=SUBJECT,
        message=MESSAGE.format(confirmation_code),
        from_email=FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )'''


def generate_short_link():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))


def generate_file(carts):
    grociries = ''
    for recipe in carts:
        recipe = recipe.recipe
        one_recipe = ''
        title = recipe.name
        items = IngredientRecipe.objects.filter(recipe=recipe)
        for item in items:
            n = item.ingredient.name
            m = item.ingredient.measurement_unit
            one_recipe += f'{n} {item.amount} {m}\n'
        grociries += f'{title}: {one_recipe}\n'
    return grociries


def generate_txt(grociries):
    with tempfile.NamedTemporaryFile(
        delete=False, mode='w', suffix='.txt'
    ) as temp_file:
        temp_file.write(grociries)
        return temp_file.name
