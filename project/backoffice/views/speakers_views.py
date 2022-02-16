import datetime
from home.models import Speaker
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.http import JsonResponse
from backoffice.serializers import SpeakerSerializer
from rest_framework.pagination import PageNumberPagination
from home.release_task import release_speaker


# Spikerlar ro'yxati
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def speakers_list(request):
    speakers = Speaker.objects.all()
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(speakers, request)
    serializer = SpeakerSerializer(
        page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

# speaker ma'lumotlari
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def speaker_detail(request, id):
    speaker = Speaker.objects.get(id=id)
    serializer = SpeakerSerializer(speaker, context={'request': request})
    return Response(serializer.data)


# spikerga ban berish
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def speaker_ban(request, id):
    speaker = Speaker.objects.filter(id=id)
    date_of_release = request.POST.get('date_of_release')
    reason_of_ban = request.POST.get('reason_of_ban')
    speaker.update(status=0, date_of_release=date_of_release, reason_of_ban=reason_of_ban)

    release_speaker()
    
    return JsonResponse({'status': 'ok'})

# spikerni karantinga yuborish
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def speaker_karantin(request, pk):
    speaker = Speaker.objects.filter(pk=pk)
    reason_of_ban = request.POST.get('reason_of_ban')
    speaker.update(status=0, reason_of_ban=reason_of_ban)

    return JsonResponse({'status': 'ok'})


