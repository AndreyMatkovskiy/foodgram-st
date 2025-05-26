from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Tag, Ingredient, Recipe,
    RecipeIngredient, Favorite, ShoppingCart
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'created_at',)
    list_display_links = ('name', 'author',)
    inlines = (RecipeIngredientInline,)
    filter_horizontal = ('tags',)

    @admin.display(
        description=format_html('<strong>Рецептов в избранных</strong>')
    )
    def in_favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe',)
    list_display_links = ('recipe',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe',)
