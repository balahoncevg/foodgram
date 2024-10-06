from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import EMAIL_LENGTH, NAME_LENGTH
from .validators import username_validators


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    username = models.CharField(
        max_length=NAME_LENGTH,
        unique=True,
        help_text=(
            'Не более 150 символов. Только буквы латиницы, цифры и @/./+/-/_.'
        ),
        verbose_name='Имя пользователя',
        validators=username_validators,
        error_messages={
            'unique': 'Имя уже занято'
        }
    )
    email = models.EmailField(
        max_length=EMAIL_LENGTH,
        unique=True,
        verbose_name='Эл. почта',
        error_messages={
            'unique': 'Для этой почты уже есть аккаунт'
        }
    )
    first_name = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='Фамилмя'
    )
    avatar = models.ImageField(
        upload_to='api/images/',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')


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
        Tag, through='TagRecipe',
        verbose_name='теги'
    )
    cooking_time = models.IntegerField(
        verbose_name='время приготовления')

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
    )


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
    )
    amount = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'ингдиенты в рецепте'


class RecipeShortLink(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    short_url = models.CharField(max_length=EMAIL_LENGTH, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_cart')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='shopping_cart')


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorite')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorite')
