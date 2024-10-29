from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from backend.constants import EMAIL_LENGTH, NAME_LENGTH

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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
