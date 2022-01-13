import datetime
import json

import requests
from django.conf import settings

from django.db.models import F
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from home.models import Users, Course, Order, Speaker
from home.serializers import OrderSerializers
from simplejwt.backends import TokenBackend
from uniredpay import models, serializers
from uniredpay.models import PayForBalance, PercentageOfSpeaker, UserSms
from uniredpay.unired_sms import sms_send

from uniredpay import uniredpay_conf

unired_url = {
    '9860': settings.UNICOIN_HOST_HUMO,
    '8600': settings.UNICOIN_HOST_UZCARD
}


# Card Register
# data = {
#     'card_number': 'karta raqami',
#     'expire': 'amal qilish vaqti'
# }
@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def card_register(request):
    url = unired_url.get(request.data.get('card_number')[:4])
    if not url:
        return Response({'result': 'Wrong card number!!!'})
    return Response(
        data=get_request_result(url=url, access_token=login(url), data=request.data, method='card.register'))


# Card Info
# data = {
#     'card_number': 'karta raqami',
#     'expire': 'amal qilish vaqti'
# }
@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def card_info(request):
    url = unired_url.get(request.data.get('card_number')[:4])
    if not url:
        return Response({'result': 'Wrong card number!!!'})
    return Response(
        data=get_request_result(url=url, access_token=login(url), data=request.data, method='card.info'))


# Card History
# data = {
#     "card_number": "9860040102963614",
#     "expire": "0526",
#     "start_date": "20210910",
#     "end_date": "20211004"
# }
@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def card_history(request):
    url = unired_url.get(request.data.get('card_number')[:4])
    if not url:
        return Response({'result': 'Wrong card number!!!'})
    return Response(
        data=get_request_result(url=url, access_token=login(url), data=request.data, method='card.history'))


# Terminal qo'shish
# data: {
#     "merchant": 'merchant_id',
#     "terminal": 'terminal_id'
# }
@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def add_terminal(request):
    merchant = request.data.get('merchant')
    if len(merchant.strip()) == 8:
        url = settings.UNICOIN_HOST_UZCARD
        data = {
            'merchant': request.data.get('merchant'),
            'terminal': request.data.get('terminal'),
            "type": 1,
            "port": 1010,
            "purpose": "Online to’lovlar amalga oshirish"
        }
    else:
        url = settings.UNICOIN_HOST_HUMO
        data = {
            "merchant": request.data.get('merchant'),
            "terminal": request.data.get('terminal'),
            "type": 1,
            "purpose": "Tolov omalga oshirish",
            "point_code": "100010104110",
            "originator": "Test Trade ",
            "centre_id": "Test eportal"
        }
    return Response(get_request_result(url=url, access_token=login(url), data=data, method='terminal.add'))


# Terminalni tekshirish
# data: {
#     "merchant": 'merchant_id',
#     "terminal": 'terminal_id'
# }
@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def check_terminal(request):
    merchant = request.data.get('merchant')
    if len(merchant.strip()) >= 15:
        url = settings.UNICOIN_HOST_HUMO
    else:
        url = settings.UNICOIN_HOST_UZCARD
    return Response(
        get_request_result(url=url, access_token=login(url), data=request.data, method='terminal.check'))


# Terminalni o'chirish
# data: {
#     "merchant": 'merchant_id',
#     "terminal": 'terminal_id'
# }
@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def remove_terminal(request):
    merchant = request.data.get('merchant')
    if len(merchant.strip()) >= 15:
        url = settings.UNICOIN_HOST_HUMO
    else:
        url = settings.UNICOIN_HOST_UZCARD
    return Response(
        get_request_result(url=url, access_token=login(url), data=request.data, method='terminal.remove'))


# Hold yaratish
# data: {
#     "card_number": 'karta raqami',
#     "expire": 'amal qilish vaqti'
#     "amount": 'miqdori'
# }
@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def hold_create(request):
    url = unired_url.get(request.data.get('card_number')[:4])
    if url == settings.UNICOIN_HOST_UZCARD:
        data = {
            "card_number": request.data.get('card_number'),
            "expire": request.data.get('expire'),
            "amount": request.data.get('amount'),
            "time": 1,
            "merchant": settings.UZCARD_MERCHANT_ID,
            "terminal": settings.UZCARD_TERMINAL_ID
        }
    else:
        data = {
            "card_number": request.data.get('card_number'),
            "expire": request.data.get('expire'),
            "amount": 100,
            "time": 60,
            "merchant": settings.HUMO_MERCHANT_ID,
            "terminal": settings.HUMO_TERMINAL_ID
        }
    return Response(
        data=get_request_result(url=url, access_token=login(url), data=data, method='hold.create'))


# Hold ni bekor qilish
# HUmo
# data: {
#     "hold_id": 'hold_id',
#     "uuid": '{uuid}'
# }
#
# Uzcard
# data = {
#     "hold_id": '{hold_id}'
# }
@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def hold_dismiss(request):
    uu_id = request.data.get('uuid')
    if uu_id:
        url = settings.UNICOIN_HOST_HUMO
    else:
        url = settings.UNICOIN_HOST_UZCARD
    return Response(data=get_request_result(url, login(url), request.data, 'hold.dismiss'))


# Hold ni amalga oshirish
# HUmo
# data: {
#     "hold_id": 'hold_id',
#     "uuid": '{uuid}'
#     "amount": midor int
# }
#
# Uzcard
# data = {
#     "hold_id": '{hold_id}'
#     "amount": int
# }
@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def hold_charge(request):
    uu_id = request.data.get('uuid')
    if uu_id:
        url = settings.UNICOIN_HOST_HUMO
    else:
        url = settings.UNICOIN_HOST_UZCARD
    return Response(data=get_request_result(url, login(url), request.data, 'hold.charge'))


@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def send_sms_to_user(request):
    user = uniredpay_conf.get_user(request)

    if not user:
        return Response({'status': False, 'error': "Validation Error"})

    serializer = serializers.UserSMSSerializers(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors)

    url = unired_url.get(serializer.validated_data['card_number'][:4])

    data = {
        "card_number": request.data.get('card_number'),
        "expire": request.data.get('expire'),
    }

    if not url:
        return Response({'result': 'Wrong card number!!!'})
    elif url == settings.UNICOIN_HOST_HUMO:
        data['merchant'] = settings.HUMO_MERCHANT_ID
        data['terminal'] = settings.HUMO_TERMINAL_ID
    else:
        data['merchant'] = settings.UZCARD_MERCHANT_ID
        data['terminal'] = settings.UZCARD_TERMINAL_ID

    data1 = get_request_result(url=url, access_token=login(url), data=data, method='card.register')

    if data1.get('status'):
        try:
            UserSms.objects.filter(user=user).delete()
            UserSms.objects.create(user=user, sms_code=sms_send(data1['result']['phone']),
                                   card_number=serializer.validated_data['card_number'],
                                   card_expire=serializer.validated_data['expire'],
                                   amount=serializer.validated_data['amount'])

            if serializer.validated_data['is_save']:
                user.card_number = serializer.validated_data['card_number']
                user.card_expire = serializer.validated_data['expire']
                user.save(update_fields=['card_number', 'card_expire'])
        except Exception as e:
            return Response({
                'status': False,
                'error': f'{e}'
            })

        return Response({
            'status': True,
            'message': f"SMS {data1['result']['phone']} telefon raqamiga jo'natildi!!!"
        })

    return Response(data1)


@api_view(['post'])
@permission_classes([])
@authentication_classes([])
def pay_for_balance(request):
    user = uniredpay_conf.get_user(request)

    if not user:
        return Response({'status': False, 'error': 'Validation Error.'})

    seria = serializers.PayForBalanceSMSSerializer(data=request.data)

    if not seria.is_valid():
        return Response(seria.errors)

    try:
        check_sms = UserSms.objects.get(user=user, sms_code=seria.validated_data['sms_code'])
    except:
        return Response({'status': False, 'error': 'SMS Code in Not Valid.'})

    if not user.wallet_number:
        return Response({'status': False, 'error': "Wallet Not Found"})

    pay_data = {
        "number": check_sms.card_number,
        "expire": check_sms.card_expire,
        "receiver": user.wallet_number,
        "amount": check_sms.amount * 100
    }

    try:
        res = uniredpay_conf.wallet_api(data=pay_data, method='transfer.proceed')
    except:
        return Response({'status': False, 'error': "Kutilmagan xatolik. Iltimos boshqatdan urunib ko'ring!!!"})

    if res['status']:
        try:
            user.cash = user.calculate_cash
            user.save()
            PayForBalance.objects.create(user=user, amount=check_sms.amount, tr_id=res['result']['tr_id'])
            UserSms.objects.filter(user=user).delete()
        except Exception as e:
            return Response({'error': f'{e}'})
        return Response({'status': True, 'message': 'Successfully'})
    return Response(res)


@api_view(['post'])
@permission_classes([])
@authentication_classes([])
def pay_to_course_from_balance(request):
    user = uniredpay_conf.get_user(request)

    if not user:
        return Response({'status': False, 'error': "validation Error."})

    seria = serializers.PayForCourseWithoutSMSSerializer(data=request.data)

    if not seria.is_valid():
        return Response({'status': False, 'error': seria.errors})

    try:
        course = Course.objects.get(id=seria.validated_data['course_id'])
        price = course.price - course.discount
    except Exception as e:
        return Response({'status': False, 'error': f'{e}'})

    if price <= user.bonus:
        try:
            user.bonus -= price
            Order.objects.create(user=user, course=course, bonus=price, discount=course.discount)
            user.save()
        except Exception as e:
            return Response({'status': False, 'error': f'{e}'})
        return Response({'status': True, 'message': 'Successfully.'})
    elif price > (user.cash + user.bonus):
        return Response({'status': False, 'message': 'Hisobingizda mablag\' yetarli emas.'})

    price -= user.bonus

    return pay_eduon_and_speaker(user=user, course=course, amount=price)


@api_view(['post'])
@permission_classes([])
@authentication_classes([])
def pay_to_course_from_card(request):
    user = uniredpay_conf.get_user(request)

    if not user:
        return Response({'status': False, 'error': "Validation Error."})

    seria = serializers.PayForCourseSMSSerializer(data=request.data)

    if not seria.is_valid():
        return Response({'status': False, 'error': seria.errors})

    try:
        user_sms = UserSms.objects.get(user=user, sms_code=seria.validated_data['sms_code'])
    except:
        return Response({'status': False, 'error': 'SMS code is Invalid.'})

    try:
        course = Course.objects.get(id=seria.validated_data['course_id'])
        price = course.price - course.discount
    except Exception as e:
        return Response({'status': False, 'error': f'{e}'})

    if not user.wallet_number:
        return Response({'status': False, 'error': "User don't have wallet!!!"})

    if price <= user.bonus:
        user.bonus -= price
        Order.objects.create(course=course, user=user, bonus=price, discount=course.discount)
        user.save()
        return Response({'status': True, 'message': 'Successfully'})
    elif price <= (user.cash + user.bonus):
        price -= user.bonus

        return pay_eduon_and_speaker(user=user, course=course, amount=price, card_number=user_sms.card_number)
    else:
        price -= user.bonus
        pay = price - user.cash

        data = {
            "number": user_sms.card_number,
            "expire": user_sms.card_expire,
            "receiver": user.wallet_number,
            "amount": pay * 100
        }

        try:
            res = uniredpay_conf.wallet_api(data=data, method='transfer.proceed')
        except:
            return Response({'status': False, 'error': "Kutilmagan xatolik. Iltimos keyinroq urinib ko'ring!!!"})

        if res['status']:
            PayForBalance.objects.create(user=user, amount=pay, tr_id=res['result']['tr_id'])
            UserSms.objects.filter(user=user).delete()

            return pay_eduon_and_speaker(user=user, course=course, amount=price, card_number=user_sms.card_number)
        return Response(res)


@api_view(['post'])
@permission_classes([])
@authentication_classes([])
def get_money_from_wallet(request):
    speaker = uniredpay_conf.get_speaker(request)

    if not speaker:
        return Response({"status": False, 'error': 'Validation Error.'})

    seria = serializers.SpeakerCardSerializers(data=request.data)

    if not seria.is_valid():
        return Response({'status': False, 'error': seria.errors})

    if speaker.cash < 50000:
        return Response({'status': False, 'error': "Hisobingizda 50 ming dan kam mablag' bor!!!"})

    data = {
        "number": speaker.wallet_number,
        "expire": speaker.wallet_expire,
        "receiver": seria.validated_data['card_number'],
        "amount": speaker.cash
    }

    try:
        res = uniredpay_conf.wallet_api(data=data, method='transfer.proceed')
    except:
        return Response({'status': False, 'error': "Kutilmagan xatolik. Iltimos keyinroq urinib ko'ring!!!"})

    if res.get('status'):
        speaker.cash = speaker.calculate_cash
        speaker.save()
        return Response({'status': True, 'message': 'Successfully'})

    return Response(res)


def pay_eduon_and_speaker(user, course, amount, card_number=None):
    speaker = course.author
    p_of_pay, create = PercentageOfSpeaker.objects.get_or_create()

    if not speaker.wallet_number:
        return Response({'status': False, 'error': "Speaker don't have wallet!!!"})

    if user.parent_ref_code == speaker.own_ref_code:
        for_speaker = amount * p_of_pay.from_own_staff / 100
        for_eduon = amount - for_speaker
    else:
        for_speaker = amount * p_of_pay.from_user / 100
        for_eduon = amount - for_speaker

    pay_sp_data = {
        "number": user.wallet_number,
        "expire": user.wallet_expire,
        "receiver": speaker.wallet_number,
        "amount": for_speaker * 100
    }

    pay_eduon_data = {
        "number": user.wallet_number,
        "expire": user.wallet_expire,
        "amount": for_eduon * 100,
        "time": 100
    }

    try:
        res_sp = uniredpay_conf.wallet_api(data=pay_eduon_data, method='hold.create')
    except:
        return Response({'status': False, 'error': "Kutilmagan xatolik. Iltimos boshqatdan urunib ko'ring!!!"})

    if res_sp.get('status'):
        res_eduon = uniredpay_conf.wallet_api(data=pay_sp_data, method='transfer.proceed')

        if res_eduon.get('status'):
            uniredpay_conf.wallet_api(data={'tr_id': res_sp['result']['tr_id']}, method='hold.charge')
            user.cash = user.calculate_cash
            speaker.cash = speaker.calculate_cash
            Order.objects.create(course=course, user=user, bonus=user.bonus, summa=amount, sp_summa=for_speaker,
                                 discount=course.discount,
                                 for_eduon=for_eduon, card_number=card_number)
            user.bonus = 0
            user.save()
            speaker.save()
            return Response({'status': True, 'message': "Successfully"})
        else:
            uniredpay_conf.wallet_api(data={'tr_id': res_sp['result']['tr_id']}, method='hold.dismiss')

    return Response(res_sp)


def login(url):
    try:
        data = dict(
            id="1",
            method="login",
            params=dict(
                login=settings.UNICOIN_LOGIN,
                password=settings.UNICOIN_PASSWORD
            )
        )
        headers = {'Content-type': 'Application/json', 'Accept': 'Application/json'}
        rq = requests.post(url, data=json.dumps(data), headers=headers)

        rsp = rq.json()
    except Exception as e:
        rsp = {
            "status": False,
            "message": "{}".format(e),
            "result": None
        }

    if rsp.get('status'):
        return rsp['result']['access_token']
    else:
        return Response(rsp)


def get_request_result(url, access_token, data, method):
    headers = {
        'Unisoft-Authorization': 'Bearer ' + access_token,
        'Content-type': 'application/json',
        'Accept': 'Application/json'
    }
    data = dict(
        id="1",
        method=method,
        params=data,
    )
    rq = requests.post(url, headers=headers, data=json.dumps(data))
    return rq.json()


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_payment_history(request):
    try:
        user = uniredpay_conf.get_user(request)
    except:
        return Response({
            "status": False,
            "error": "Validation Error"
        })

    data = models.PayForBalance.objects.filter(user=user)
    serial_data = serializers.PayForBalanceSerializers(data, many=True)

    return Response(serial_data.data)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_course_orders(request):
    try:
        user = uniredpay_conf.get_user(request)
    except:
        return Response({
            "status": False,
            "error": "Validation Error"
        })

    data = Order.objects.filter(user=user)
    serial_data = OrderSerializers(data, many=True)

    return Response(serial_data.data)
