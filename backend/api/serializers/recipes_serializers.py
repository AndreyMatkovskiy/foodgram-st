from rest_framework import serializers
from api.fileds import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework.exceptions import ValidationError


MIN_VALUE = 1
MAX_VALUE = 32000


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientInRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE
    )


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_author(self, obj):
        from api.serializers.users_serializers import UserSerializer
        return UserSerializer(obj.author, context=self.context).data

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_ingredients(self, obj):
        return [{
            'id': recipe_ingredient.ingredient.id,
            'name': recipe_ingredient.ingredient.name,
            'measurement_unit': recipe_ingredient.ingredient.measurement_unit,
            'amount': recipe_ingredient.value
        } for recipe_ingredient in obj.ingredients_for_the_recipe.all()]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.shopping_carts.filter(recipe=obj).exists()
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        write_only=True,
        required=True
    )
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError("Нужен хотя бы один ингредиент")
        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError("Ингредиенты не должны дублироваться")
        existing_ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        if existing_ingredients.count() != len(ingredient_ids):
            existing_ids = set(
                existing_ingredients.values_list('id', flat=True)
            )
            missing_ids = set(ingredient_ids) - existing_ids
            raise ValidationError(f"Несуществующие ингредиенты: {missing_ids}")
        return value

    def _create_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=item['id'],
                value=item['amount']
            ) for item in ingredients_data
        ])

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        user = (
            validated_data.pop('author', None) or self.context['request'].user
        )
        recipe = Recipe.objects.create(author=user, **validated_data)
        self._create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        if ingredients_data is None:
            raise ValidationError(
                {"ingredients": "Это поле обязательно при обновлении"}
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.ingredients_for_the_recipe.all().delete()
        self._create_ingredients(instance, ingredients_data)
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
