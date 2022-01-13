from rest_framework.response import Response
from rest_framework.views import APIView

from home.models import Users, Speaker
from . import models, serializers
from .uniredpay_conf import create_speaker_wallet, create_user_wallet, get_user, get_speaker, wallet_api

'''
Online Card Create
"login": "Eduon",
"password": "Nr9WAVeS1TjV"
'''


class CreateWalletUserAndSpeakersCLass(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        no_w_users = Users.objects.filter(wallet_number__isnull=True, first_name__isnull=False, last_name__isnull=False)
        no_w_speaker = Speaker.objects.filter(wallet_number__isnull=True, speaker__first_name__isnull=False,
                                              speaker__last_name__isnull=False)

        try:
            for user in no_w_users:
                create_user_wallet(user.first_name, user.last_name, user.phone)

            for sp in no_w_speaker:
                create_speaker_wallet(sp.speaker.first_name, sp.speaker.last_name, sp.phone)
        except:
            return Response({'status': False, 'error': 'Aniqlanmagan xatolik'})

        return Response({'status': True, 'message': 'Muvoffaqiyatli amalga oshirildi!!!'})

    def post(self, request):
        try:
            res = wallet_api(data={}, method='wallet.balance')
        except Exception as e:
            return Response({'status': False, 'error': f'{e}'})

        return Response(res)


class CreateOnlineCardForUser(APIView):

    def get(self, request):
        user = get_user(request)
        return create_user_wallet(user.first_name, user.last_name, user.phone)

    def post(self, request):
        try:
            user = get_user(request)
            cash = user.calculate_cash
        except Exception as e:
            return Response({'status': False, 'error': e})

        return Response({'status': True, 'message': 'Successfully Updated'})

    def put(self, request):
        try:
            user = get_user(request)
            serial = serializers.CardHistorySerializers(data=request.data)

            if not serial.is_valid():
                return Response(serial.errors)

            if not user.wallet_number:
                return Response({'status': False, 'error': "Online wallet not found"})

            data = {
                'number': user.wallet_number,
                'expire': user.wallet_expire,
                'start_date': serial.validated_data['start_date'].strftime('%Y%m%d'),
                'end_date': serial.validated_data['end_date'].strftime('%Y%m%d')
            }

            res = wallet_api(data=data, method='wallet.history')

            return Response(res)
        except Exception as e:
            return Response({'status': False, 'error': f'{e}'})


class CreateOnlineCardForSpeaker(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            speaker = get_speaker(request)
            create_speaker_wallet(speaker.speaker.first_name, speaker.speaker.last_name, speaker.phone)
        except Exception as e:
            return Response({'status': False, 'error': e})

        return Response({'status': True, 'message': 'Successfully Created'})

    def post(self, request):
        try:
            speaker = get_speaker(request)
            cash = speaker.calculate_cash
        except Exception as e:
            return Response({'status': False, 'error': e})

        return Response({'status': True, 'message': 'Successfully Update'})

    def put(self, request):
        try:
            speaker = get_speaker(request)
            serial = serializers.CardHistorySerializers(data=request.data)

            if not serial.is_valid():
                return Response(serial.errors)

            if not speaker.wallet_number:
                return Response({'status': False, 'error': "Online wallet not found"})

            data = {
                'number': speaker.wallet_number,
                'expire': speaker.wallet_expire,
                'start_date': serial.validated_data['start_date'].strftime('%Y%m%d'),
                'end_date': serial.validated_data['end_date'].strftime('%Y%m%d')
            }

            res = wallet_api(data=data, method='wallet.history')

            return Response(res)
        except Exception as e:
            return Response({'status': False, 'error': f'{e}'})
