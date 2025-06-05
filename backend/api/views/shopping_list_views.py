from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from ..serializers.shopping_list_serializers import ShortShoppingCartSerializer


class ShoppingCartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, recipe_id=None):
        try:
            recipe_id = int(recipe_id)
        except (TypeError, ValueError):
            return Response(
                {"error": "Неверный ID рецепта"},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.user.shopping_carts.filter(recipe=recipe).exists():
            return Response(
                {"error": "Рецепт уже в корзине"},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.user.shopping_carts.create(recipe=recipe)
        serializer = ShortShoppingCartSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, recipe_id=None):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        cart_item = request.user.shopping_carts.filter(recipe=recipe).first()
        if not cart_item:
            return Response(
                {"error": "Рецепт не был в корзине"},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
