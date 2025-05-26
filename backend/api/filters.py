from django_filters import rest_framework as filters
from recipes.models import Recipe, Ingredient
from django_filters import CharFilter
from django_filters.rest_framework import FilterSet


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__identifier')
    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_shopping')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__author=self.request.user)
        else:
            return queryset

    def filter_shopping(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_cart__author=self.request.user)
        else:
            return queryset
