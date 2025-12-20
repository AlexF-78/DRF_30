from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsModerator(BasePermission):
    """Проверка, является ли пользователь модератором"""

    def has_permission(self, request, view):
        # Проверяем, авторизован ли пользователь
        if not request.user or not request.user.is_authenticated:
            return False

        # Проверяем, входит ли пользователь в группу 'moderators'
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(BasePermission):
    """Проверка, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы для всех авторизованных
        if request.method in SAFE_METHODS:
            return True

        # Проверяем, есть ли у объекта поле owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrModerator(BasePermission):
    """Проверка, является ли пользователь владельцем или модератором"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Модераторы имеют доступ ко всем объектам
        if request.user.groups.filter(name='moderators').exists():
            return True

        # Владельцы имеют доступ к своим объектам
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False
