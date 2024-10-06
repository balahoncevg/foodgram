from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return user.is_admin


class IsAuthor(permissions.BasePermission):
    """
    Проверка на авторство.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.username == request.user


class ReadOnly(permissions.BasePermission):
    """
    Только для чтения.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class AdminOrReadOnly(permissions.BasePermission):
    """
    Проверяет является ли пользователь админом и
    если нет, то разрешает только чтение.
    """

    def has_permission(self, request, view):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        elif user.is_authenticated:
            return user.is_admin
        return False
