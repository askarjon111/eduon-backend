import json

import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .paycom import Paycom
from .exceptions import PaycomException
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes


# Create your views here.
@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def payment_view(request):
    paycom = Paycom(request)
    try:
        response = paycom.launch()
    except PaycomException as e:
        response = {
            "result": "",
            "error": {
                "code": e.ERRORS_CODES[e.code],
                "message": e.message,
                "data": ""
            }
        }

        if 'id' in paycom.params:
            response['id'] = paycom.params['id']

    return Response(response)
