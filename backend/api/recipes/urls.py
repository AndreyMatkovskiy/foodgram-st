from django.urls import include, path
from rest_framework import routers
from .views import TagViewSet, RecipeViewSet, IngredientViewSet

router = routers.DefaultRouter()
router.register('tags', TagViewSet, 'tag')
router.register('recipes', RecipeViewSet, 'recipe')
router.register('ingredients', IngredientViewSet, 'ingredient')

urlpatterns = [
    path('', include(router.urls)),
]
