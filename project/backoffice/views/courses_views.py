from django.http import JsonResponse
from home.models import Course, Discount
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from backoffice.serializers import CourseDetailSerializer, CourseListSerializer
from backoffice.permissions import OwnerPermission, AdminPermission, ManagerPermission
from home.tasks import delete_discount

# Kurslar ro'yxati
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission or AdminPermission or ManagerPermission])
def course_list(request):
    courses = Course.objects.filter(is_confirmed=True).order_by('-id')
    paginator = PageNumberPagination()
    paginator.page_size = 12
    page = paginator.paginate_queryset(courses, request)
    serializer = CourseListSerializer(
        page, many=True, context={'request': request})
    return paginator.get_pagindiscounated_response(serializer.data)


# kurs ma'lumotlari
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission or AdminPermission or ManagerPermission])
def course_detail(request, id):
    course = Course.objects.get(id=id)
    course_details = CourseDetailSerializer(course, context={'request': request})

    data = {
        "course_details": course_details.data,
    }

    return Response(data)


# kursni karantinga yuborish
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission or AdminPermission or ManagerPermission])
def course_karantin(request, id):
    course = Course.objects.filter(id=id)
    course.update(is_confirmed=False)

    return JsonResponse({'status': 'ok'})


# set discount to course

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission or AdminPermission or ManagerPermission])
def set_discount_to_course(request):
    data = request.data
    course = Course.objects.filter(id=data['course_id'])
    course.update(discount=data['discount'])
    Discount.objects.create(course=course[0], discount=data['discount'], expire_day=data['expire_day'])
    
    delete_discount()

    return JsonResponse({'status': f'discount added to {course}'})