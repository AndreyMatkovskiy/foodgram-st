from rest_framework import viewsets, permissions
from recipes.models import Tag, Ingredient, Recipe
from django_filters.rest_framework import DjangoFilterBackend
from api.recipes.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer
)
from api.permissions import IsAuthorOrReadOnly
from api.filters import RecipeFilter, IngredientFilter
from api.paginations import Pagination
from rest_framework.decorators import action
from rest_framework.response import Response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filterset_class = RecipeFilter
    pagination_class = Pagination

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        recipe.favorites.create(author=request.user)
        return Response(status=201)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        recipe.shoppingcart_set.create(author=request.user)
        return Response(status=201)
