import json

import requests

from eduon import settings


def sms_login():
    r = requests.post(settings.SMS_BASE_URL + '/api/auth/login/',
                      {'email': settings.SMS_EMAIL, 'password': settings.SMS_SECRET_KEY}).json()
    settings.SMS_TOKEN = r['data']['token']


def sms_refresh():
    r = requests.patch(settings.SMS_BASE_URL + '/api/auth/refresh',
                       headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'}).json()
    settings.SMS_TOKEN = r['data']['token']


def sms_send(phone_number, text):
    phone_number = str(phone_number)
    phone_number.replace("+", "")
    try:
        if phone_number[0:3] == "998":
            result = requests.post(settings.SMS_BASE_URL + '/api/message/sms/send',
                                   {'mobile_phone': phone_number, 'message': text},
                                   headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'}).json()

            return result
        else:
            payload = {
                "message": text,
                "to": "+" + str(phone_number),
                "sender_id": "EduOn"
            }
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + settings.SMS_TOKEN_GLOBAL
            }
            result = requests.post('https://api.sms.to/sms/send', json.dumps(payload),
                                   headers=headers).json()
            return result

    except:
        return None
