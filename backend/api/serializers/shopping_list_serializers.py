from rest_framework import serializers
from shopping_list.models import ShoppingCart
from recipes.models import Recipe


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'user',
            'recipe'
        )
        read_only_fields = ('user',)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
