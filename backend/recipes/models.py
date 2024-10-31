from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import EMAIL_LENGTH, MAX_INT, MIN_INT, NAME_LENGTH


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
                MAX_INT,
                message=f'Время приготовления не должно быть больше {MAX_INT}.'
            ),
            MinValueValidator(
                MIN_INT,
                message=f'Время приготовления не должно быть меньше {MIN_INT}.'
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
        default=1,
        validators=[
            MaxValueValidator(
                MAX_INT,
                message=f'Объем ингредиента не должен быть больше {MAX_INT}.'
            ),
            MinValueValidator(
                MIN_INT,
                message=f'Объем ингредиента не должен быть меньше {MIN_INT}.'
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
