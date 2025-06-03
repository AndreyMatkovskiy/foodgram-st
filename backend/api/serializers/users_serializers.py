from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from users.models import Subscription
from recipes.models import Recipe
import re

User = get_user_model()


def validate_username(value):
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise serializers.ValidationError(
            'Username содержит недопустимые символы.'
        )
    return value


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_avatar(self, obj):
        if obj.avatar:
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return None

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(
            follower=request.user,
            following=obj
        ).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=150,
        validators=[
            validate_username,
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        return data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        from api.serializers.recipes_serializers import ShortRecipeSerializer
        recipes = obj.recipes.all()
        limit = self.context['request'].query_params.get('recipes_limit')
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
