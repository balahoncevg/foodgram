from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class IsAuthor(permissions.BasePermission):
    """
    Проверка на авторство.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
