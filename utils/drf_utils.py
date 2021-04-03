from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Pagination class for DEFAULT_PAGINATION_CLASS rest_framework settings.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000
