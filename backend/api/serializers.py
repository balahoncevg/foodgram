import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response

from .models import (Favorite, Follow, Ingredient, IngredientRecipe,
                     Recipe, ShoppingCart, Tag, TagRecipe)


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'avatar', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = self.context['request'].user
            return Follow.objects.filter(user=user, author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngrdientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('amount', 'id', 'measurement_unit', 'name')


class TagRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tag.id'
    )
    name = serializers.CharField(
        source='tag.name',
        read_only=True
    )
    slug = serializers.SlugField(
        source='tag.slug',
        read_only=True
    )

    class Meta:
        model = TagRecipe
        fields = ('id', 'name', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)
    tags = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text',
            'ingredients', 'tags', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )
        read_only_fields = ('author', 'is_in_shopping_cart', 'is_favorited')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_tags(self, obj):
        tags = [
            {
                'id': tr['id'],
                'name': tr['name'],
                'slug': tr['slug']
            } for tr in TagRecipeSerializer(
                obj.tagrecipe_set.all(), many=True
            ).data
        ]
        return tags

    def get_ingredients(self, obj):
        ingredients = [
            {
                'id': ir['id'],
                'name': ir['name'],
                'measurement_unit': ir['measurement_unit'],
                'amount': ir['amount']
            } for ir in IngrdientRecipeSerializer(
                obj.ingredientrecipe_set.all(), many=True
            ).data
        ]
        return ingredients

    def validation_of_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'поле "ingredients" должно быть заполнено'
            )
        ingredient_ids = []
        for ingredient in ingredients:
            if 'id' not in ingredient or 'amount' not in ingredient:
                raise serializers.ValidationError(
                    'поля ингредиента не заполнены'
                )
            try:
                Ingredient.objects.get(
                    id=ingredient['id']
                )
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    'ингредиент не существует'
                )
            if int(ingredient['amount']) < 1:
                raise serializers.ValidationError(
                    'ингредиент не может быть в количестве менбше 1'
                )
            if int(ingredient['id']) in ingredient_ids:
                raise serializers.ValidationError(
                    'ингредиенты повторяются'
                )
            ingredient_ids.append(ingredient['id'])
        return ingredients

    def validation_of_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'значение тегов не должно быть пустым'
            )
        tag_ids = []
        for tag_id in tags:
            try:
                Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(
                    'тег не существует'
                )
            if tag_id in tag_ids:
                raise serializers.ValidationError(
                    'теги повторяются'
                )
            tag_ids.append(tag_id)
        return tags

    def validation_of_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'время приготовления не может быть ниже 1'
            )
        return cooking_time

    def create(self, data):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                'поле ингредиенты обязательно'
            )
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                'поле теги обязательно'
            )
        if 'image' not in self.initial_data:
            raise serializers.ValidationError(
                'поле image обязательно'
            )
        ingredienst_data = self.initial_data.get('ingredients')
        self.validation_of_ingredients(ingredienst_data)

        tag_data = self.initial_data.get('tags')
        td = list(tag_data)
        print(td)
        self.validation_of_tags(td)

        ct_data = self.initial_data.get('cooking_time')
        self.validation_of_cooking_time(ct_data)

        recipe = Recipe.objects.create(**data)
        for ingredient_data in ingredienst_data:
            if int(ingredient_data['amount']) < 1:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            try:
                ingredient = get_object_or_404(Ingredient, id=ingredient_data['id'])
                IngredientRecipe.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )
            except Http404:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        for one_tag_data in tag_data:
            try:
                tag = get_object_or_404(Tag, id=one_tag_data)
                TagRecipe.objects.create(
                    tag=tag,
                    recipe=recipe
                )
            except Http404:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return recipe

    def update(self, instance, validated_data):
        ingredienst_data = self.initial_data.get('ingredients')
        self.validation_of_ingredients(ingredienst_data)
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                'поле теги обязательно'
            )
        tag_data = self.initial_data.get('tags')
        td = list(tag_data)
        print(td)
        self.validation_of_tags(td)
        ct_data = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        self.validation_of_cooking_time(ct_data)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()

        if ingredienst_data:
            IngredientRecipe.objects.filter(
                recipe=instance
            ).delete()
            for ingredient_data in ingredienst_data:
                ingredient = Ingredient.objects.get(
                    id=ingredient_data['id']
                )
                IngredientRecipe.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )
        if tag_data:
            TagRecipe.objects.filter(recipe=instance).delete()
            for one_tag_data in tag_data:
                tag = Tag.objects.get(id=one_tag_data)
                TagRecipe.objects.create(
                    tag=tag,
                    recipe=instance
                )
        return instance


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')
        read_only_fields = ('user', 'recipe')


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')
        read_only_fields = ('user', 'recipe')


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('id', 'user', 'author')
        read_only_fields = ('user', 'author')
