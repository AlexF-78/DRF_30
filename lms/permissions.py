from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsModerator(BasePermission):
    """
    Разрешение, проверяющее, является ли пользователь модератором.
    Пользователь считается модератором, если он состоит в группе 'moderators'.
    """

    def has_permission(self, request, view):
        """
        Проверяет, авторизован ли пользователь и принадлежит ли он к группе 'moderators'.

        Args:
            request (Request): Объект HTTP-запроса.
            view (View): Представление, к которому применяется разрешение.

        Returns:
            bool: True, если пользователь авторизован и входит в группу 'moderators', иначе False.
        """
        # Проверяем, авторизован ли пользователь
        if not request.user or not request.user.is_authenticated:
            return False

        # Проверяем, входит ли пользователь в группу 'moderators'
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(BasePermission):
    """
    Разрешение, проверяющее, является ли пользователь владельцем объекта.
    Для безопасных методов (GET, HEAD, OPTIONS) разрешение автоматически.
    Для остальных методов требуется, чтобы пользователь был владельцем объекта.
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, является ли текущий пользователь владельцем объекта.

        Args:
            request (Request): Объект HTTP-запроса.
            view (View): Представление, к которому применяется разрешение.
            obj (object): Объект ресурса, к которому применяется разрешение. Предполагается, что у объекта есть поле 'owner'.

        Returns:
            bool: True, если пользователь владелец объекта или запрос является безопасным; иначе False.
        """
        # Для безопасных методов (чтение) разрешение выдается всем авторизованным
        if request.method in SAFE_METHODS:
            return True

        # Проверяем наличие у объекта поля owner и сравниваем его с текущим пользователем
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        # Если у объекта нет поля owner, то разрешение отвергается
        return False


class IsOwnerOrModerator(BasePermission):
    """
    Разрешение, позволяющее доступ либо владельцу объекта, либо модераторам.

    Поведение:
    - Для разрешения доступа на уровне общих разрешений (например, при проверке доступа к странице):
      разрешает только авторизованным пользователям.
    - Для проверки конкретного объекта (например, при выполнении операции с конкретным элементом):
      разрешает:
        - всем модераторам, независимо от владельца
        - владельцам объектов, если они связаны с этим объектом (имеют поле 'owner')

    Используется для ограничения доступа к ресурсам, где важна роль и право владения.
    """

    def has_permission(self, request, view):
        """Проверяет, авторизован ли пользователь."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """ Проверяет, имеет ли пользователь право доступа к конкретному объекту."""
        # Проверяем, является ли текущий пользователь модератором
        if request.user.groups.filter(name='moderators').exists():
            return True

        # Владельцы имеют доступ к своим объектам
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False
