import json
from django.http import JsonResponse
import requests

from eduon import settings


def sms_login():
    r = requests.post(settings.SMS_BASE_URL + '/api/auth/login/',
                      {'email': settings.SMS_EMAIL, 'password': settings.SMS_SECRET_KEY}).json()
    settings.SMS_TOKEN = r['data']['token']


def sms_login_global():
    r = requests.post(settings.SMS_BASE_URL_GLOBAL + '/oauth/token',
                {'client_id': settings.SMS_CLIENT_ID, 'secret': settings.SMS_SECRET_KEY_GLOBAL,
                 "expires_in": 3600}).json()
    print(r)
    settings.SMS_TOKEN_GLOBAL = r['jwt']


def sms_refresh():
    r = requests.patch(settings.SMS_BASE_URL + '/api/auth/refresh',
                       headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'}).json()
    settings.SMS_TOKEN = r['data']['token']


def sms_send(phone_number, text):
    try:
        phone_number = str(phone_number)
        phone_number.replace("+", "")
        if phone_number[0:3] == "998":
            sms_login()
            result = requests.post(settings.SMS_BASE_URL + '/api/message/sms/send',
                                   {'mobile_phone': phone_number, 'message': text},
                                   headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'}).json()

            return result
        else:
            sms_login_global()
            payload = {
                "message": text,
                "to": "+" + str(phone_number),
                "sender_id": "EduOn"
            }
            print(payload)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + settings.SMS_TOKEN_GLOBAL
            }
            result = requests.post('https://api.sms.to/sms/send', json.dumps(payload),
                                   headers=headers).json()
            return result
    except Exception as e:
        data = {
            "success": False,
            "message": "{}".format(e)
        }
        return JsonResponse(data)
