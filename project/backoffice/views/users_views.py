from home.models import Order, Users
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.http import JsonResponse
from backoffice.serializers import PayForBalanceSerializer, UserSerializer
from rest_framework.pagination import PageNumberPagination
from home.release_task import release_user
from home.serializers import OrderSerializers
from uniredpay.models import PayForBalance
from backoffice.permissions import OwnerPermission, AdminPermission, ManagerPermission


# Foydalanuvchilar ro'yxati
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | AdminPermission | ManagerPermission])
def users_list(request):
    users = Users.objects.all()
    paginator = PageNumberPagination()
    paginator.page_size = 12
    page = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(
        page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# user ma'lumotlari
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | AdminPermission | ManagerPermission])
def user_detail(request, id):
    user = Users.objects.get(id=id)
    user_details = UserSerializer(user, context={'request': request})
    orders = Order.objects.filter(user=id).order_by('-date')
    orders = OrderSerializers(orders, many=True, context={'request': request})
    pay_for_balances = PayForBalance.objects.filter(user=id).order_by('-date')
    pay_for_balances = PayForBalanceSerializer(pay_for_balances, many=True)

    data = {
        "user_details": user_details.data,
        "orders": orders.data,
        "pay_for_balances": pay_for_balances.data,
    }

    return Response(data)


# userga ban berish
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | AdminPermission | ManagerPermission])
def user_ban(request, id):
    user = Users.objects.filter(id=id)
    date_of_release = request.POST.get('date_of_release')
    user.update(is_active=False, date_of_release=date_of_release,)

    release_user()

    return JsonResponse({'status': 'ok'})


# userni karantinga yuborish
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | AdminPermission | ManagerPermission])
def user_karantin(request, id):
    user = Users.objects.filter(id=id)
    reason_of_ban = request.POST.get('reason_of_ban')
    user.update(is_active=False, reason_of_ban=reason_of_ban)

    return JsonResponse({'status': 'ok'})


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | AdminPermission | ManagerPermission])
def user_bonus(request, id):
    user = Users.objects.get(id=id)
    bonus = request.POST.get('bonus')
    user.bonus += int(bonus)
    user.save()

    return JsonResponse({'status': 'ok'})
    