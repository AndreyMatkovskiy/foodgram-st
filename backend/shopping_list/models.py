from django.db import models
from django.conf import settings
from recipes.models import Recipe


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_carts',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_item'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в корзину'
