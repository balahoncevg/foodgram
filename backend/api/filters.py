import django_filters

from .models import Ingredient, Recipe, Tag, TagRecipe


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
    tags = django_filters.CharFilter(method='filter_tags')
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_tags(self, queryset, name, value):
        tags = self.request.query_params.getlist('tags')
        print(tags)
        validated_tags = []
        if tags:
            validated_tags = []
            for tag in tags:
                current_tag = Tag.objects.get(slug=tag)
                if len(TagRecipe.objects.filter(tag=current_tag)) > 0:
                    print(TagRecipe.objects.filter(tag=current_tag))
                    validated_tags.append(tag)
                    print(validated_tags)
            first_tag = validated_tags.pop()
            result = queryset.filter(tags__slug=first_tag)
            for v_tag in validated_tags:
                result = result.union(queryset.filter(tags__slug=v_tag))
            return result
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if value == 1:
            return queryset.filter(is_favorited=True)
        elif value == 0:
            return queryset.filter(is_favorited=False)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == 1:
            return queryset.filter(is_in_shopping_cart=True)
        elif value == 0:
            return queryset.filter(is_in_shopping_cart=False)
        return queryset
