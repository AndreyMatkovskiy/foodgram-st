from django.urls import reverse
from rest_framework import viewsets, permissions, status
from recipes.models import RecipeIngredient, Tag, Ingredient, Recipe
from django_filters.rest_framework import DjangoFilterBackend
from api.serializers.recipes_serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateUpdateSerializer
)
from api.permissions import IsAuthorOrReadOnly
from api.filters import RecipeFilter, IngredientFilter
from api.paginations import Pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.text import slugify
from collections import defaultdict
from api.serializers.favorite_serializers import ShortFavoriteSerializer
from api.serializers.shopping_list_serializers import (
    ShortShoppingCartSerializer
)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related(
        'ingredients_for_the_recipe__ingredient',
        'favorited_by',
        'in_carts'
    ).all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_object(self):
        try:
            recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        except Recipe.DoesNotExist:
            raise NotFound({"detail": "Рецепт не найден"})
        self.check_object_permissions(self.request, recipe)
        return recipe

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def create(self, request, *args, **kwargs):
        create_serializer = RecipeCreateUpdateSerializer(
            data=request.data,
            context={'request': request}
        )
        create_serializer.is_valid(raise_exception=True)
        recipe = create_serializer.save(author=request.user)
        read_serializer = RecipeSerializer(
            recipe,
            context={'request': request}
        )
        return Response(
            data=read_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        output_serializer = RecipeSerializer(
            instance,
            context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user and not request.user.is_staff:
            return Response(
                {"error": "У вас нет прав для удаления этого рецепта"},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=[permissions.AllowAny],
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        relative_url = reverse('recipes-detail', args=[recipe.id])
        full_url = request.build_absolute_uri(relative_url)
        return Response({'short-link': full_url}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            if user.favorites.filter(recipe=recipe).exists():
                return Response(
                    {"error": "Рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.favorites.create(recipe=recipe)
            serializer = ShortFavoriteSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = user.favorites.filter(recipe=recipe).first()
        if not favorite:
            return Response(
                {"error": "Рецепт не был в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            if user.shopping_carts.filter(recipe=recipe).exists():
                return Response(
                    {"error": "Рецепт уже в корзине"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.shopping_carts.create(recipe=recipe)
            serializer = ShortShoppingCartSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        cart_item = user.shopping_carts.filter(recipe=recipe).first()
        if not cart_item:
            return Response(
                {"error": "Рецепт не был в корзине"},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RecipeSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = RecipeSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        user = request.user
        shopping_carts = user.shopping_carts.select_related('recipe').all()
        recipe_ids = [cart.recipe_id for cart in shopping_carts]
        if not recipe_ids:
            return Response(
                {"error": "Список покупок пуст"},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe_names = [cart.recipe.name for cart in shopping_carts]
        if len(recipe_names) == 1:
            recipe_name = recipe_names[0]
            safe_name = slugify(recipe_name)[:50]
            filename = f'Список_покупок_для_рецепта_{safe_name}.txt'
        else:
            filename = f'Список_покупок_для_{len(recipe_names)}_рецептов.txt'
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe_id__in=recipe_ids)
            .select_related('ingredient')
            .order_by('ingredient__name')
        )
        ingredient_totals = defaultdict(float)
        for item in ingredients:
            key = (
                f"{item.ingredient.name} "
                f"({item.ingredient.measurement_unit})"
            )
            ingredient_totals[key] += float(item.value)
        text = 'Список покупок:\n\n'
        text += f"Рецепты: {', '.join(recipe_names)}\n\n"
        text += "Ингредиенты:\n"
        for key, total_amount in sorted(ingredient_totals.items()):
            if total_amount.is_integer():
                total_amount = int(total_amount)
            text += f"- {key} - {total_amount}\n"
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
