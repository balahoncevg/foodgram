import io
import random
import string

from recipes.models import IngredientRecipe


def generate_short_link():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))


def generate_file(carts):
    groceries = []
    for grocery in carts:
        recipe = grocery.recipe
        items = IngredientRecipe.objects.filter(recipe=recipe)
        for item in items:
            groceries.append([
                item.ingredient.name,
                item.amount,
                item.ingredient.measurement_unit
            ])
    final_grocieries = {}
    grocieries_names = []
    for grocery in groceries:
        if grocery[0] not in grocieries_names:
            grocieries_names.append(grocery[0])
            final_grocieries.update(
                {grocery[0]: [grocery[1], grocery[2]]}
            )
        else:
            final_grocieries[grocery[0]][0] += grocery[1]
    final_grocieries = sorted(final_grocieries.items())
    grocieries_to_print = ''
    for grocery in final_grocieries:
        am = grocery[1][0]
        mu = grocery[1][1]
        grocieries_to_print += f'{grocery[0]} - {am} {mu}\n'

    file_buffer = io.StringIO()
    file_buffer.write(grocieries_to_print)
    file_buffer.seek(0)
    return file_buffer
