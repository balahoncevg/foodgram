from typing import Any
from django.contrib import admin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import Favorite, Ingredient, Recipe, Tag, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar'
    )
    list_editable = (
        'email',
        'first_name',
        'last_name',
        'avatar'
    )
    search_fields = (
        'username',
        'email',
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)


class FavoriteInLine(admin.StackedInline):
    model = Favorite
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    inlines = (FavoriteInLine,)
    list_display = (
        'name',
        'author'
    )
    search_fields = (
        'name',
        'author'
    )
    # list_filter = ('tags',)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favorited=Count('favorite'))


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )


admin.site.register(User, UserAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
