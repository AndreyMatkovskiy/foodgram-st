from recipes.models import Recipe, Ingredient
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet, CharFilter


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__id'
    )
    author = filters.NumberFilter(
        field_name='author__id'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_in_shopping_cart',
            'is_favorited'
        )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user or not user.is_authenticated:
            return queryset.none()
        if value:
            return queryset.filter(favorited_by__user=user)
        return queryset.exclude(favorited_by__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user or not user.is_authenticated:
            return queryset.none()
        if value:
            return queryset.filter(in_carts__user=user)
        return queryset.exclude(in_carts__user=user)
