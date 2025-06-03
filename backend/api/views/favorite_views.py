from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from ..serializers.favorite_serializers import ShortRecipeSerializer


class FavoriteViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, recipe_id=None):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.user.favorites.filter(recipe=recipe).exists():
            return Response(
                {"error": "Рецепт уже в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.user.favorites.create(recipe=recipe)
        serializer = ShortRecipeSerializer(
            recipe,
            context={'request': request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, recipe_id=None):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        favorite = request.user.favorites.filter(recipe=recipe).first()
        if not favorite:
            return Response(
                {"error": "Рецепт не был в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
