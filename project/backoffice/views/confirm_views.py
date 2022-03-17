from django.http import JsonResponse
from home.models import Course
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from backoffice.serializers import CourseListSerializer
from backoffice.permissions import OwnerPermission, AdminPermission, ManagerPermission

# tasdiqlanmagan kurslar
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | AdminPermission | ManagerPermission])
def unconfirmed_courses(request):
    courses = Course.objects.filter(is_confirmed=False, is_banned=False).order_by('-id')
    paginator = PageNumberPagination()
    paginator.page_size = 12
    page = paginator.paginate_queryset(courses, request)
    serializer = CourseListSerializer(
        page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# kursni tasdiqlash / karantindan chiqarish
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | AdminPermission | ManagerPermission])
def course_confirm(request, id):
    course = Course.objects.filter(id=id)
    course.update(is_confirmed=True)

    return JsonResponse({'status': 'ok'})


# kursni karantinga yuborish
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | AdminPermission | ManagerPermission])
def course_ban(request, id):
    course = Course.objects.get(id=id)
    course.is_banned=True
    course.is_confirmed=False
    course.save()

    return JsonResponse({'status': f"{course.name} banned"})
