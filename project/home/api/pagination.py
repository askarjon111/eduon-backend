from rest_framework import pagination
from rest_framework.response import Response


class CourseCustomPagination(pagination.PageNumberPagination):
    page_size = 9

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'num_pages': self.page.paginator.num_pages,
            'results': data
        })
