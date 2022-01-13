import json
import random
import re

import requests

from eduon import settings


def sms_login():
    r = requests.post(settings.SMS_BASE_URL + '/api/auth/login/',
                      {'email': settings.SMS_EMAIL, 'password': settings.SMS_SECRET_KEY}).json()
    return r['data']['token']


def sms_send(phone_number):
    phone_number = str(phone_number)
    phone_number = ''.join(
        re.findall(r'\+?(\d{3})[\s-]?[(]?(\d{2})[)]?[-\s]?(\d{3})[-\s]?(\d{2})[-\s]?(\d{2})', phone_number)[0])
    code = random.randint(100000, 999999)
    try:
        if phone_number[:3] == "998":
            result = requests.post(settings.SMS_BASE_URL + '/api/message/sms/send',
                                   {'mobile_phone': phone_number,
                                    'message': text.format(code)},
                                   headers={'Authorization': f'Bearer {sms_login()}'}).json()

            return code
        else:
            payload = {
                "message": text.format(code),
                "to": "+" + str(phone_number),
                "sender_id": "EduOn"
            }
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + settings.SMS_TOKEN_GLOBAL
            }
            result = requests.post('https://api.sms.to/sms/send', json.dumps(payload),
                                   headers=headers).json()
            return code

    except:
        return None


text = """
Eduon.uz tasdiqlash kodi: {}
(Hech kimga aytmang! Firibgarlardan ehtiyot bo'ling.)
"""
