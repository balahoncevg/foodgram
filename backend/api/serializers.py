from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MaxValueValidator, MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.constants import (
    MAX_COOCING_TIME,
    MAX_INGREDIENT_AMOUNT,
    MIN_COOCING_TIME,
    MIN_INGREDIENT_AMOUNT
)
from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Follow


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)
    password = serializers.CharField(
        write_only=True, required=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'avatar', 'is_subscribed', 'password')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        user = request.user
        return user.is_authenticated and Follow.objects.filter(
            user=user, author=obj
        ).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('is_create'):
            representation.pop('is_subscribed', None)
            representation.pop('avatar', None)
            self.context.pop('is_create', None)
            return representation
        request = self.context.get('request')
        if request is None:
            representation['avatar'] = None
        elif instance.avatar and hasattr(instance.avatar, 'url'):
            representation['avatar'] = request.build_absolute_uri(
                instance.avatar.url
            )
        else:
            representation['avatar'] = None
        return representation

    def validate(self, attrs):
        if self.instance is None and 'password' not in attrs:
            raise serializers.ValidationError(
                {'password': 'Обязательное поле.'}
            )
        request = self.context.get('request')
        if request and request.method == 'PUT':
            if not request.data:
                raise serializers.ValidationError(
                    'Поле "avatar" должно присутствовать в запросе.'
                )
        return attrs

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        self.context['is_create'] = True
        return user


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тегов.
    Создавать новые теги может только администратор.
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиентов.
    Создавать новые ингредиенты может только администратор.
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngrdientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связывающей модели рецепт-ингредиент."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message=f'Ингредиентов - не менее {MIN_INGREDIENT_AMOUNT}!'),
            MaxValueValidator(
                MAX_INGREDIENT_AMOUNT,
                message=f'Ингредиентов - не более {MAX_INGREDIENT_AMOUNT}!')
        ]
    )

    class Meta:
        model = IngredientRecipe
        fields = ('amount', 'id', 'measurement_unit', 'name')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngrdientRecipeSerializer(
        source='ingredientrecipe_set', many=True,
        read_only=True
    )
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.image and hasattr(instance.image, 'url'):
            representation['image'] = request.build_absolute_uri(
                instance.image.url
            )
        else:
            representation['image'] = None
        return representation


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания, редактирования и удаления рецептов.
    Создать рецепт можно только с использованием
    добавленных администратором тегов и ингредиентов.
    """

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngrdientRecipeSerializer(
        source='ingredientrecipe_set', many=True,
    )
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

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Поле "ингредиенты" обязательно.'
            )
        ingredient_ids = []
        for ingredient in ingredients:
            ingredient_id = ingredient['ingredient'].id
            if not ingredient:
                raise serializers.ValidationError(
                    'Отсутствует поле "id" для ингредиента.'
                )
            if 'amount' not in ingredient:
                raise serializers.ValidationError(
                    'Отсутствует поле "amount" для ингредиента.'
                )
            if not Ingredient.objects.filter(
                id=ingredient_id
            ).exists():
                raise serializers.ValidationError(
                    'Указан несуществующий ингредиент.'
                )
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
            ingredient_ids.append(ingredient_id)
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Поле "теги" обязательно.'
            )
        tag_ids = []
        for tag in tags:
            if not Tag.objects.filter(
                id=tag.id
            ).exists():
                raise serializers.ValidationError(
                    'Указан несуществующий тег.'
                )
            if tag.id in tag_ids:
                raise serializers.ValidationError(
                    'Теги не должны повторяться.'
                )
            tag_ids.append(tag.id)
        return tags

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < MIN_COOCING_TIME:
            raise serializers.ValidationError(
                f'Время приготовления не может быть меньше {MIN_COOCING_TIME}.'
            )
        if int(cooking_time) > MAX_COOCING_TIME:
            raise serializers.ValidationError(
                f'Время приготовления не может быть больше {MAX_COOCING_TIME}.'
            )
        return cooking_time

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Изображение обязательно.'
            )
        return image

    def validate(self, attrs):
        if 'image' not in attrs:
            raise serializers.ValidationError(
                'Изображение обязательно.'
            )
        if 'tags' not in attrs:
            raise serializers.ValidationError(
                'Поле "теги" обязательно.'
            )
        if 'ingredientrecipe_set' not in attrs:
            raise serializers.ValidationError(
                'Поле "ингредиенты" обязательно.'
            )
        return attrs

    def create_ingredient_recipe(self, ingredients_data, recipe):
        ingredient_recipe_bounds = []
        for ingredient_data in ingredients_data:
            ingredient_recipe_bounds.append(IngredientRecipe(
                recipe=recipe, ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            ))
        IngredientRecipe.objects.bulk_create(ingredient_recipe_bounds)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredientrecipe_set')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredient_recipe(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        if self.context.get('request').user != instance.author:
            raise serializers.ValidationError(
                'Пользователь не может редактировать чужие рецепты.'
            )
        ingredients_data = validated_data.pop('ingredientrecipe_set')
        tags_data = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        instance.ingredients.clear()
        self.create_ingredient_recipe(ingredients_data, instance)
        instance.tags.set(tags_data)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.image and hasattr(instance.image, 'url'):
            representation['image'] = request.build_absolute_uri(
                instance.image.url
            )
        else:
            representation['image'] = None
        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True).data
        return representation


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для списка избранного."""

    id = serializers.IntegerField(source='author.id', read_only=True)
    email = serializers.CharField(
        source='author.email', read_only=True
    )
    username = serializers.CharField(
        source='author.username', read_only=True)
    first_name = serializers.CharField(
        source='author.first_name', read_only=True)
    last_name = serializers.CharField(
        source='author.last_name', read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        return True

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.author.avatar and hasattr(obj.author.avatar, 'url'):
            return request.build_absolute_uri(obj.author.avatar.url)
        return None

    def get_recipes(self, obj):
        limit = self.context.get(
            'request'
        ).query_params.get('recipes_limit')
        recipes = obj.author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        recipes_data = RecipeReadSerializer(
            recipes, many=True, context=self.context
        ).data
        for recipe_data in recipes_data:
            recipe_data.pop('author', None)
            recipe_data.pop('text', None)
            recipe_data.pop('ingredients', None)
            recipe_data.pop('tags', None)
            recipe_data.pop('is_favorited', None)
            recipe_data.pop('is_in_shopping_cart', None)
        return recipes_data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')

    def validate(self, data):
        if ShoppingCart.objects.filter(
            user=data['user'], recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок.'
            )
        return data

    def create(self, validated_data):
        return ShoppingCart.objects.create(**validated_data)

    def to_representation(self, instance):
        recipe = instance.recipe
        request = self.context.get('request')
        image_url = request.build_absolute_uri(recipe.image.url)
        return {
            'id': recipe.id,
            'name': recipe.name,
            'image': image_url,
            'cooking_time': recipe.cooking_time}


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного."""

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')
        read_only_fields = ('user', 'recipe')

    def validate(self, data):
        if Favorite.objects.filter(
            user=data['user'], recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список избранное.'
            )
        return data

    def create(self, validated_data):
        return Favorite.objects.create(**validated_data)

    def to_representation(self, instance):
        recipe = instance.recipe
        request = self.context.get('request')
        image_url = request.build_absolute_uri(recipe.image.url)
        return {
            'id': recipe.id,
            'name': recipe.name,
            'image': image_url,
            'cooking_time': recipe.cooking_time}


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )

    class Meta:
        model = Follow
        fields = ('id', 'user', 'author')
        read_only_fields = ('user', 'author')

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if Follow.objects.filter(
            user=data['user'], author=data['author']
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        return data

    def create(self, validated_data):
        return Follow.objects.create(**validated_data)
