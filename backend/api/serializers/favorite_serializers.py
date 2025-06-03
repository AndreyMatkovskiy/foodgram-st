from rest_framework import serializers
from recipes.models import Recipe
from favorites.models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    image = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.recipe.image and request:
            return request.build_absolute_uri(obj.recipe.image.url)
        return None


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
