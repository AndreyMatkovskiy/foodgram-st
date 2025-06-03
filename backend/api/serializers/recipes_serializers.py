from rest_framework import serializers
from api.fileds import Base64ImageField
from api.serializers.users_serializers import UserSerializer
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from favorites.models import Favorite
from shopping_list.models import ShoppingCart
from rest_framework.exceptions import ValidationError


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


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
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

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
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
        if not user or not user.is_authenticated:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user or not user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    ingredients = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate_tags(self, value):
        if not value:
            raise ValidationError("Нужно выбрать хотя бы один тег.")
        existing_tags = Tag.objects.filter(id__in=value)
        if len(existing_tags) != len(value):
            existing_ids = set(existing_tags.values_list('id', flat=True))
            missing_ids = set(value) - existing_ids
            raise ValidationError(
                f"Несуществующие теги: {missing_ids}"
            )
        return value

    def validate_ingredients(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise ValidationError("Нужен хотя бы один ингредиент")
        valid_ids = set()
        for ing in value:
            if 'id' not in ing or 'amount' not in ing:
                raise ValidationError("Неверный формат ингредиентов")
            try:
                ing_id = int(ing['id'])
                amount = int(ing['amount'])
            except (TypeError, ValueError):
                raise ValidationError("Неверный формат ингредиентов")
            if amount < 1:
                raise ValidationError("Количество должно быть положительным")
            if ing_id in valid_ids:
                raise ValidationError(f"Ингредиент {ing_id} дублируется")
            valid_ids.add(ing_id)
        existing_ingredients = Ingredient.objects.filter(id__in=valid_ids)
        existing_ids = set(existing_ingredients.values_list('id', flat=True))
        missing_ids = valid_ids - existing_ids
        if missing_ids:
            raise ValidationError(
                f"Несуществующие ингредиенты: {missing_ids}"
            )
        return value

    def create(self, validated_data):
        validated_data.pop('author', None)
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)
        if tags_data:
            recipe.tags.set(Tag.objects.filter(id__in=tags_data))
        for item in ingredients_data:
            ingredient_id = item.get('id')
            ingredient_name = item.get('name')
            amount = item.get('amount')
            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist:
                raise ValidationError(
                    f"Ингредиент {ingredient_name} не найден"
                )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                value=amount
            )
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)
        if ingredients_data is None:
            raise ValidationError(
                {"ingredients": "Это поле обязательно при обновлении"}
            )
        instance.name = validated_data.get(
            'name',
            instance.name
        )
        instance.text = validated_data.get(
            'text',
            instance.text
        )
        instance.image = validated_data.get(
            'image',
            instance.image
        )
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.save()
        if tags_data is not None:
            instance.tags.set(Tag.objects.filter(id__in=tags_data))
        instance.ingredients_for_the_recipe.all().delete()
        for item in ingredients_data:
            ingredient_id = item.get('id')
            ingredient_name = item.get('name')
            amount = item.get('amount')
            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist:
                raise ValidationError(
                    f"Ингредиент {ingredient_name} не найден"
                )
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                value=amount
            )
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
