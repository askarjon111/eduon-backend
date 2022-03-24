from backoffice.permissions import AdminPermission, ManagerPermission, OwnerPermission
from backoffice.serializers import CourseListSerializer, SpeakerSerializer, UserSerializer
from home.models import Course, Speaker, Users
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from home.serializers import UsersSerializer


# Karantin
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | AdminPermission | ManagerPermission])
def karantin(request):
    query = request.GET.get('query')
    paginator = PageNumberPagination()
    if query == 'speakers':
        speakers = Speaker.objects.filter(status=0)
        # speakers_page = paginator.paginate_queryset(speakers, request)
        speakers = SpeakerSerializer(speakers, many=True)
        data = {
            "speakers": speakers.data,
        }


    elif query == 'courses':
        courses = Course.objects.filter(is_banned=True).order_by('-id')
        # courses_page = paginator.paginate_queryset(courses, request)
        courses = CourseListSerializer(
            courses, many=True)

        data = {
            "courses": courses.data,
        }


    elif query == 'users':
        users = Users.objects.filter(
            is_active=False, date_of_release=None).order_by('-id')
        # users_page = paginator.paginate_queryset(users, request)
        users = UserSerializer(
            users, many=True)

        data = {
            "users": users.data,
        }


    elif query == 'all':
        speakers = Speaker.objects.filter(status=0)
        # speakers_page = paginator.paginate_queryset(speakers, request)
        speakers = SpeakerSerializer(speakers, many=True)

        users = Users.objects.filter(
            is_active=False, date_of_release=None).order_by('-id')
        # users_page = paginator.paginate_queryset(users, request)
        users = UserSerializer(
            users, many=True)

        courses = Course.objects.filter(is_banned=True).order_by('-id')
        # courses_page = paginator.paginate_queryset(courses, request)
        courses = CourseListSerializer(
            courses, many=True)

        data = {
            "speakers": speakers.data,
            "users": users.data,
            "courses": courses.data,
        }
    else:
        data = {
            "message": "Noto'g'ri query yuborildi"
        }
        return Response(data)

    return Response(data)
