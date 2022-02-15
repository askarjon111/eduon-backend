import datetime
from home.models import Speaker
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.http import JsonResponse
from backoffice.serializers import SpeakersListSerializer
from rest_framework.pagination import PageNumberPagination


# Spikerlar ro'yxati
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def speakers_list(request):
    speakers = Speaker.objects.all()
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(speakers, request)
    serializer = SpeakersListSerializer(
        page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)