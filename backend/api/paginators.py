from rest_framework.pagination import PageNumberPagination

from backend.constants import MAX_PAGE_SIZE, PAGE_SIZE


class PageLimitPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
    max_page_size = MAX_PAGE_SIZE
