from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (GetRecipeShortLink,
                    IngredientViewSet, RecipeViewSet, SubscibeAndDescribe,
                    SubscriptionsView, TagViewSet,
                    UserViewSet, AddAndDeleteAvatar)
# UsersViewSet, AddAndDeleteAvatar, ApiSendTokenView, ApiUserCreateView,)


app_name = 'api'

api_v1 = DefaultRouter()
api_v1.register(r'users', UserViewSet, basename='users')
api_v1.register(r'recipes', RecipeViewSet, basename='recipes')
api_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
api_v1.register(r'tags', TagViewSet, basename='tags')


urlpatterns = [
    path('', include(api_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:id>/get-link/', GetRecipeShortLink.as_view(),
         name='get_recipe_link'),
    path('users/<int:id>/subscribe/',
         SubscibeAndDescribe.as_view(),
         name='subscribe_and_describe'),
    path('users/me/avatar/', AddAndDeleteAvatar.as_view(),
         name='add_and_delete_avatar'),
    path('users/subscriptions/', SubscriptionsView.as_view(),
         name='subscriptions')
]
