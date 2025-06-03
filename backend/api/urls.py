from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.users_views import UserViewSet
from .views.recipes_views import RecipeViewSet, IngredientViewSet, TagViewSet
from .views.shopping_list_views import ShoppingCartViewSet
from .views.favorite_views import FavoriteViewSet

router = DefaultRouter()
router.register(
    'users',
    UserViewSet,
    basename='users'
)
router.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    'shopping-carts',
    ShoppingCartViewSet,
    basename='shopping-carts'
)

urlpatterns = [
    path(
        '',
        include(router.urls)
    ),
    path(
        'shopping-carts/add/<int:recipe_id>/',
        ShoppingCartViewSet.as_view({'post': 'create'}),
        name='shopping-cart-add'
    ),
    path(
        'shopping-carts/remove/<int:recipe_id>/',
        ShoppingCartViewSet.as_view({'delete': 'destroy'}),
        name='shopping-cart-remove'
    ),
    path(
        'shopping-carts/download/',
        ShoppingCartViewSet.as_view({'get': 'download'}),
        name='shopping-cart-download'
    ),
    path(
        'favorites/add/<int:recipe_id>/',
        FavoriteViewSet.as_view({'post': 'create'}),
        name='favorite-add'
    ),
    path(
        'favorites/remove/<int:recipe_id>/',
        FavoriteViewSet.as_view({'delete': 'destroy'}),
        name='favorite-remove'
    ),
    path(
        'auth/',
        include('djoser.urls')
    ),
    path(
        'auth/',
        include('djoser.urls.authtoken')
    ),
]
