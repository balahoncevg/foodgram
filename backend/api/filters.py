import django_filters

from django.db.models import Exists, OuterRef, Value

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(
        field_name='author__id'
    )
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                )
            )
        else:
            queryset = queryset.annotate(
                is_favorited=Value(False))
        if value == 1:
            return queryset.filter(is_favorited=True)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                )
            )
        else:
            queryset = queryset.annotate(
                is_in_shopping_cart=Value(False))
        if value == 1:
            return queryset.filter(is_in_shopping_cart=True)
        return queryset
