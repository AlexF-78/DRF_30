import re

from rest_framework.exceptions import ValidationError


def validate_youtube_url(value):
    """
    Валидатор, разрешающий только ссылки на youtube.
    :param value: трока с ссылкой
    :raises ValidationError: если ссылка не соответствует формату youtube
    """
    # Удаление лишних пробелов
    value = value.strip()
    # Регулярное выражение для проверки ссылок youtube
    youtube_regex = (
        r"^(https?\:\/\/)?(www\.youtube\.com\/(watch\?v=|embed\/|v\/|.+\?v=)|"
        r"youtu\.be\/)([a-zA-Z0-9_-]{11})(\S*)?$"
    )
    if not re.match(youtube_regex, value):
        raise ValidationError("Можно использовать только ссылки на YouTube.")
