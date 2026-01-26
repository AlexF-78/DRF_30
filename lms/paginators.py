from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = "page_size"  # Параметр для изменения количества элементов
    max_page_size = 100  # Максимальное количество элементов на странице
