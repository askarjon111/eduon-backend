from backoffice.permissions import AdminPermission, ManagerPermission, OwnerPermission
from backoffice.serializers import CourseListSerializer
from home.models import Course, Speaker, Users
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# Karantindagi spikerlar
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission or AdminPermission or ManagerPermission])
def karantindagi_kurslar(request):
    courses = Course.objects.filter(is_banned=True).order_by('-id')
    paginator = PageNumberPagination()
    paginator.page_size = 12
    page = paginator.paginate_queryset(courses, request)
    serializer = CourseListSerializer(
        page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)