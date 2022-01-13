import json, requests

from django.contrib.auth.models import User
from rest_framework.response import Response

from home import models as home_model
from simplejwt.backends import TokenBackend

BASE_URL = 'https://wallet.unired.uz/api/v1/gw'


def get_user(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        valid_data = TokenBackend(algorithm='HS256').decode(token, verify=False)
        user = home_model.Users.objects.get(id=valid_data['user_id'])
    except:
        return None

    return user


def get_speaker(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        valid_data = TokenBackend(algorithm='HS256').decode(token, verify=False)
        user = User.objects.get(id=valid_data['user_id'])
        speaker = home_model.Speaker.objects.get(speaker=user)
    except:
        return None

    return speaker


# todo: yaratilgan user uchun elektron hamyon yaratish
def create_user_wallet(first_name, last_name, phone):
    data = {
        'name': f'{first_name} {last_name}',
        'phone': phone,
        'wallet_name': f'{first_name} {last_name}'
    }

    res = wallet_api(data, 'wallet.create')
    if res.get('status'):
        users = home_model.Users.objects.filter(phone=phone).update(
            wallet_number=res['result']['card_number'],
            wallet_expire=res['result']['expire'])
        if users:
            return Response({'status': True, 'message': 'Online hisob raqam yaratildi!!!'})
        else:
            return Response({'status': False, 'message': "Hechqanday foydalanuvchi yangilanmadi"})
    else:
        return Response(res)


# todo: yaratilgan speaker uchun elektron hamyon yaratish
def create_speaker_wallet(first_name, last_name, phone):
    data = {
        'name': f'{first_name} {last_name}',
        'phone': phone,
        'wallet_name': f'{first_name} {last_name}'
    }

    res = wallet_api(data, 'wallet.create')
    if res.get('status'):
        users = home_model.Speaker.objects.filter(phone=phone, wallet_number__isnull=True).update(
            wallet_number=res['result']['card_number'],
            wallet_expire=res['result']['expire'])
        if users:
            return Response({'status': True, 'message': 'Online hisob raqam yaratildi!!!'})
        else:
            return Response({'status': False, 'message': "Hechqanday foydalanuvchi yangilanmadi"})
    else:
        return Response(res)


def wallet_api(data: dict, method: str):
    res = get_token()

    if res['status']:

        access_token = res['result']['access_token']
        headers = {
            'Unisoft-Authorization': f'Bearer {access_token}',
            'Content-type': 'application/json',
            'Accept': 'Application/json',
            'token': access_token
        }

        d = {
            "id": "2",
            "method": method,
            "params": data
        }

        rq = requests.post(BASE_URL, headers=headers, data=json.dumps(d))
        return rq.json()
    else:
        return Response(res)


def get_token():
    headers = {
        'Content-type': 'application/json',
        'Accept': 'Application/json'
    }

    data = {
        "id": "1",
        "method": "partner.login",
        "params": {
            "username": "eduon",
            "password": "Nr9WAVeS1TjV"
        }
    }
    try:
        res = requests.post(url='https://wallet.unired.uz/api/v1/gw', headers=headers, data=json.dumps(data))

        response = res.json()
    except Exception as e:
        response = {
            "status": False,
            "message": "{}".format(e),
            "result": None
        }

    return response
