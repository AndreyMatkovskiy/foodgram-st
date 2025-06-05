from django.db import models
from django.conf import settings
from .abstract_models import AuthorCreatedModel
from django.core.validators import MaxValueValidator, MinValueValidator

MIN_COOKING_TIME = 1
MAX_LEN_RECIPE = 256
MAX_VALUE = 32000
MIN_INGREDIENT_VALUE = 1


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Уникальный слаг'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Количество'
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
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    image = models.ImageField(
        verbose_name='Фото рецепта',
        upload_to='recipes/'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=MAX_LEN_RECIPE
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                f'Значение должно быть не меньше {MIN_COOKING_TIME}'
            ),
            MaxValueValidator(
                MAX_VALUE,
                f'Значение должно быть больше {MAX_VALUE}'
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
                MIN_INGREDIENT_VALUE,
                f'Значение должно быть не меньше {MIN_INGREDIENT_VALUE}'
            ),
            MaxValueValidator(
                MAX_VALUE,
                f'Значение должно быть не больше {MAX_VALUE}'
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
