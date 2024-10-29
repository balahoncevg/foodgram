import os

from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeShortLink, ShoppingCart, Tag)
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    FavoriteSerializer, FollowSerializer, IngredientSerializer,
    RecipeCreateUpdateSerializer, RecipeReadSerializer,
    ShoppingCartSerializer, SubscriptionSerializer,
    TagSerializer, UserSerializer)

from .paginators import PageLimitPagination
from .permissions import (IsAuthor)
from .utils import generate_file, generate_short_link, generate_txt


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageLimitPagination

    def get_serializer_context(self):
        '''Используется для передачи данных о пользователе.'''
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(
        detail=False, methods=['get'],
        permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response(UserSerializer(
            request.user, context={'request': request}).data)

    @action(
        detail=False, methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        follows = Follow.objects.filter(
            user=self.request.user
        ).select_related('author')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(follows, request)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


class AddAndDeleteAvatar(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        if not request.data:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserSerializer(
            request.user, data=request.data,
            context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'avatar': serializer.data['avatar']})
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ['name']
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    http_method_names = ('get', 'list')


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    http_method_names = ('get', 'list')


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'patch', 'post', 'delete']
    serializer_class = RecipeReadSerializer
    pagination_class = PageLimitPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeCreateUpdateSerializer
        return RecipeReadSerializer

    def get_permissions(self):
        if self.action in [
            'destroy', 'update', 'partial_update'
        ] and self.request.user.is_authenticated:
            permission_classes = [IsAuthor]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def get(self, request):
        carts = ShoppingCart.objects.filter(
            user=self.request.user
        ).select_related('recipe')
        grociries = generate_file(carts)
        file_path = generate_txt(grociries)
        response = FileResponse(
            open(file_path, 'rb'), as_attachment=True,
            filename='ingredients.txt')
        os.remove(file_path)
        return response

    @action(
        detail=True, methods=['post',],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            data = {'recipe': recipe.id,
                    'user': request.user.id}
            serializer = ShoppingCartSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            image_url = request.build_absolute_uri(recipe.image.url)
            return Response(
                {
                    'id': recipe.id,
                    'name': recipe.name,
                    'image': image_url,
                    'cooking_time': recipe.cooking_time},
                status=status.HTTP_201_CREATED
            )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            shopping_cart = get_object_or_404(
                ShoppingCart, recipe=recipe,
                user=request.user
            )
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=['post',],
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            data = {'recipe': recipe.id,
                    'user': request.user.id}
            serializer = FavoriteSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            image_url = request.build_absolute_uri(recipe.image.url)
            return Response(
                {
                    'id': recipe.id,
                    'name': recipe.name,
                    'image': image_url,
                    'cooking_time': recipe.cooking_time},
                status=status.HTTP_201_CREATED
            )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        try:
            favorite = get_object_or_404(
                Favorite, recipe=recipe, user=request.user)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetRecipeShortLink(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        short_link, created = RecipeShortLink.objects.get_or_create(
            recipe=recipe, defaults={'short_url': generate_short_link()}
        )
        link = f'https://myuniquehotsname.zapto.org/{short_link.short_url}'
        return Response({'short-link': link}, status=status.HTTP_200_OK)


class SubscibeAndDescribe(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageLimitPagination

    def post(self, request, id):
        author = get_object_or_404(User, id=id)
        data = {'author': author.id, 'user': request.user.id}
        serializer = FollowSerializer(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        this_follow = Follow.objects.get(
            author=author.id, user=request.user.id
        )
        outer_serializer = SubscriptionSerializer(
            this_follow, context={'request': request}
        )
        return Response(outer_serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        try:
            follow = get_object_or_404(
                Follow, author=author, user=request.user)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(status=status.HTTP_400_BAD_REQUEST)
