from django.db import models
from django.conf import settings


class AuthorModel(models.Model):
    # Абстрактная модель автора (связь объект + автор)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class AuthorCreatedModel(AuthorModel):
    # Абстрактная модель даты создания (автор + дата)
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True
