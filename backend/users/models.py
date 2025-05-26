from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(
        max_length=50,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия'
    )
    username = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Почта пользователя'
    )
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    follower = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчики'
    )
    following = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Подписан на'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )
