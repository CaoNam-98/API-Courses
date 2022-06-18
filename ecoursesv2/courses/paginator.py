from rest_framework.pagination import PageNumberPagination

# Lấy 20 item
class BasePaginator(PageNumberPagination):
    # page_size = 20 là trên 1 trang có 20 item
    page_size = 2