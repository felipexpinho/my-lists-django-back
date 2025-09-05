from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

class ProductPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view)
        except NotFound:
            # Página fora do range: criar uma "página vazia"
            self.page = []
            return []

    def get_paginated_response(self, data):
        # Se self.page for lista vazia, simula count e links
        if isinstance(self.page, list):
            return Response({
                'count': 0,
                'next': None,
                'previous': None,
                'results': []
            })
        return super().get_paginated_response(data)