from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.constants import EMAIL_LENGTH, NAME_LENGTH

from .constants import (
    DEFAULT_INGREDIENT_AMOUNT,
    MAX_COOCING_TIME,
    MAX_INGREDIENT_AMOUNT,
    MIN_COOCING_TIME,
    MIN_INGREDIENT_AMOUNT
)


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=NAME_LENGTH,
        unique=True,
        verbose_name='имя'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='слаг'
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='имя'
    )
    measurement_unit = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='единица измерения'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient'
            )
        ]
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='автор'
    )
    name = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='имя'
    )
    image = models.ImageField(
        upload_to='api/images/',
        verbose_name='картинка'
    )
    text = models.TextField(verbose_name='текст')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe',
        verbose_name='ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipes',
        verbose_name='теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления',
        validators=[
            MaxValueValidator(
                MAX_COOCING_TIME,
                message=('Время приготовления '
                         f'не должно быть больше {MAX_COOCING_TIME}.')
            ),
            MinValueValidator(
                MIN_COOCING_TIME,
                message=('Время приготовления '
                         f'не должно быть меньше {MIN_COOCING_TIME}.')
            )
        ])

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        default=DEFAULT_INGREDIENT_AMOUNT,
        validators=[
            MaxValueValidator(
                MAX_INGREDIENT_AMOUNT,
                message=('Объем ингредиента не должен '
                         f'быть больше {MAX_INGREDIENT_AMOUNT}.')
            ),
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message=('Объем ингредиента не должен '
                         f'быть меньше {MIN_INGREDIENT_AMOUNT}.')
            )])

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'ингдиенты в рецепте'


class RecipeShortLink(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    short_url = models.CharField(max_length=EMAIL_LENGTH, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CartsAndLikes(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='%(model_name)s')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='%(model_name)s')

    class Meta:
        abstract = True


class ShoppingCart(CartsAndLikes):
    pass


class Favorite(CartsAndLikes):
    pass
