import os
import tempfile

from django.contrib.auth.tokens import default_token_generator
from django.db.models import (BooleanField, Case, Exists,
                              IntegerField, OuterRef, Value, When)
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from djoser.views import UserViewSet as DjoserUserViewSet
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientFilter, RecipeFilter
from .models import (
    Favorite, Follow, Ingredient, IngredientRecipe, Recipe,
    RecipeShortLink, ShoppingCart, Tag, User)
from .serializers import (
    AvatarSerializer,
    FavoriteSerializer, FollowSerializer,
    IngredientSerializer, IngrdientRecipeSerializer,
    RecipeSerializer, ShoppingCartSerializer,
    TagSerializer, UserSerializer,)

from .paginators import CustomLimitPagination
from .permissions import (
    AdminOrReadOnly, AdminPermission, IsAuthor, ReadOnly, IsUser)
from .utils import generate_short_link, send_confirmation_code


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomLimitPagination

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(
        detail=False, methods=['get'],
        permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(request.user)
        data = serializer.data
        if request.user.avatar and hasattr(request.user.avatar, 'url'):
            avatar_url = request.build_absolute_uri(
                request.user.avatar.url) if request.user.avatar.url else None
            data.update(
                {'is_subscribed': False, 'avatar': avatar_url})
            return Response(data)
        else:
            data.update(
                {'is_subscribed': False, 'avatar': None})
            return Response(data)

    '''@action(detail=False, methods=['put', 'delete'],
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)'''

    def create(self, request, *args, **kwargs):
        data = request.data
        if 'password' not in data.keys():
            return Response(
                {'password': 'Обязательное поле.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = User(
            email=data['email'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        user.set_password(data['password'])
        user.save()

        response_data = {
            'email': user.email,
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        if instance.avatar:
            data['avatar'] = request.build_absolute_uri(
                instance.avatar.uri
            )
        else:
            data['avatar'] = None
        return Response(data)

    def list(self, request, *args, **kwargs):
        queryset = User.objects.all()
        page = self.paginate_queryset(queryset)
        data = []
        for user_instance in page:
            user_data = {
                'id': user_instance.id,
                'username': user_instance.username,
                'email': user_instance.email,
                'first_name': user_instance.first_name,
                'last_name': user_instance.last_name,

            }
            if user_instance.avatar and hasattr(
                user_instance.avatar, 'url'
            ):
                user_data['avatar'] = request.build_absolute_uri(
                    user_instance.avatar.url
                )
            else:
                user_data['avatar'] = None
            data.append(user_data)
        return self.get_paginated_response(data)


class AddAndDeleteAvatar(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        if not request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'avatar': serializer.data['avatar']})
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ['name']
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    http_method_names = ('get', 'list')

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    http_method_names = ('get', 'list')

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'patch', 'post', 'delete']
    serializer_class = RecipeSerializer
    pagination_class = CustomLimitPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            permission_classes = [IsAuthor]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()

        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                )
            )
        else:
            queryset = queryset.annotate(
                is_favorited=Value(False),
                is_in_shopping_cart=Value(False))

        tags = self.request.query_params.get('tags')
        if tags:
            tags = tags.split(',')
            queryset = queryset.filter(
                tags__slug__in=tags
            ).distinct()

        return queryset

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class.get_ingredients(
            self.serializer_class, self.get_object()
        )
        self.serializer_class.get_tags(
            self.serializer_class, self.get_object()
        )
        return super().retrieve(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['get',],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def get(self, request):
        grociries = ''
        carts = ShoppingCart.objects.filter(
            user=self.request.user
        ).select_related('recipe')
        for recipe in carts:
            recipe = recipe.recipe
            one_recipe = ''
            title = recipe.name
            items = IngredientRecipe.objects.filter(recipe=recipe)
            for item in items:
                one_recipe += f'{item.ingredient.name} {item.amount} {item.ingredient.measurement_unit}\n'
            grociries += f'{title}: {one_recipe}\n'
        file_path = self.generate_txt(grociries)
        response = FileResponse(
            open(file_path, 'rb'), as_attachment=True,
            filename='ingredients.txt')
        os.remove(file_path)
        return response

    def generate_txt(self, grociries):
        with tempfile.NamedTemporaryFile(
            delete=False, mode='w', suffix='.txt'
        ) as temp_file:
            temp_file.write(grociries)
            return temp_file.name

    @action(
        detail=True, methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def manage_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            shopping_cart, created = ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            image_url = request.build_absolute_uri(
                recipe.image.url
            ) if recipe.image else None
            return Response(
                {
                    'id': recipe.id,
                    'name': recipe.name,
                    'image': image_url,
                    'cooking_time': recipe.cooking_time
                }, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
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
        detail=True, methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def manage_favorites(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST
                )
            image_url = request.build_absolute_uri(
                recipe.image.url) if recipe.image else None
            return Response(
                {
                    'id': recipe.id,
                    'name': recipe.name,
                    'image': image_url,
                    'cooking_time': recipe.cooking_time
                },
                status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            try:
                favorite = get_object_or_404(
                    Favorite, recipe=recipe, user=request.user)
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Http404:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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
    permission_classes = [IsAuthenticated,]
    pagination_class = CustomLimitPagination

    def post(self, request, id):
        print('fffffffffffffffffffffffffffffffff')
        author = get_object_or_404(User, id=id)
        if author == request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        follow, created = Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
        if not created:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        avatar_url = request.build_absolute_uri(
            author.avatar.url) if author.avatar and hasattr(
                author.avatar, 'url') else None
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            recipes = author.recipes.all()[:recipes_limit]
        else:
            recipes = author.recipes.all()
        recipes_serialised = RecipeSerializer(
            recipes, many=True).data
        return Response(
            {
                'email': author.email,
                'id': author.id,
                'username': author.username,
                'first_name': author.first_name,
                'last_name': author.last_name,
                'is_subscribed': True,
                'recipes': recipes_serialised,
                'recipes_count': author.recipes.count(),
                'avatar': avatar_url,
            }, status=status.HTTP_201_CREATED
        )

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        try:
            follow = get_object_or_404(Follow, author=author)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitPagination

    def get(self, request):
        follows = Follow.objects.filter(
            user=self.request.user
        )
        result = []
        for follow in follows:
            author_data = ({
                'email': follow.author.email,
                'id': follow.author.id,
                'username': follow.author.username,
                'first_name': follow.author.first_name,
                'last_name': follow.author.last_name,
                'is_subscribed': True,
                'recipes': [
                    {
                        'id': recipe.id,
                        'name': recipe.name,
                        'cooking_time': recipe.cooking_time
                    } for recipe in follow.author.recipes
                ],
                'recipes_count': follow.author.recipes.count(),
            })
            result.append(author_data)
        return Response(result, status=status.HTTP_200_OK)
