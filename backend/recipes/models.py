from django.conf import settings
from django.db import models
from .abstract_models import AuthorCreatedModel
from django.core.validators import MaxValueValidator, MinValueValidator


min_cooking_time = 1
max_len_recipe = 256
max_value = 32000
min_ingredient_value = 1


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тэга'
    )

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_measurement_unit'
            )
        ]
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(AuthorCreatedModel):
    image = models.ImageField(
        verbose_name='Фото рецепта',
        upload_to='recipes/'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=max_len_recipe
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки',
        validators=[
            MinValueValidator(
                min_cooking_time,
                f'Значение должно быть не меньше {min_cooking_time}'
            ),
            MaxValueValidator(
                max_value,
                f'Значение должно быть больше {max_value}'
            )
        ]
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги для рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient'
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    value = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        validators=[
            MinValueValidator(
                min_ingredient_value,
                f'Значение должно быть не меньше {min_ingredient_value}'
            ),
            MaxValueValidator(
                max_value,
                f'Значение должно быть не больше {max_value}'
            )
        ]
    )

    class Meta:
        default_related_name = 'ingredients_for_the_recipe'
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='name_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} - {self.value}'

    @classmethod
    def shopping(cls, user):
        return (
            cls.objects.filter(
                models.Q(recipe__in=user.shopping_cart.values('recipe'))
            )
            .values(name=models.F('ingredient__name'))
            .annotate(
                unit=models.F('ingredient__measurement_unit'),
                count=models.Sum('amount'),
            )
            .order_by('ingredient__name')
        )


class Favorite(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт'
    )

    class Meta:
        default_related_name = 'favorites'
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.author.username} добавил {self.recipe.name} в избранное'


class ShoppingCart(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='in_carts',
        verbose_name='Рецепт'
    )

    class Meta:
        default_related_name = 'shopping_cart'
        verbose_name = 'корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique_cart_item'
            )
        ]

    def __str__(self):
        return f'{self.author.username} добавил {self.recipe.name} в корзину'
