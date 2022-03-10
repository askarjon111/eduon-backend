from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import Q
from backoffice.permissions import OwnerPermission, AdminPermission, ManagerPermission
from backoffice.serializers import PaymentHistorySerializer, PayForBalanceSerializer, OrderSerializer
from home.models import Order, PaymentHistory
from uniredpay.models import PayForBalance

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | AdminPermission | ManagerPermission])
def kirim_chiqim(request):
    query = request.GET.get('query')

    if query == 'all':
        paginator = PageNumberPagination()
        paginator.page_size = 4
        transactions = PaymentHistory.objects.all().order_by('-date')
        transaction_page = paginator.paginate_queryset(transactions, request)
        transactions = PaymentHistorySerializer(
            transaction_page, many=True, context={'request': request})

        orders = Order.objects.filter(Q(summa__gt=0)).order_by('-date')
        order_page = paginator.paginate_queryset(orders, request)
        orders = OrderSerializer(
            order_page, many=True, context={'request': request})

        payforbalances = PayForBalance.objects.all().order_by('-date')
        payforbalance_page = paginator.paginate_queryset(
            payforbalances, request)
        payforbalances = PayForBalanceSerializer(
            payforbalance_page, many=True, context={'request': request})
        
        data = {
            "transactions": transactions.data,
            "orders": orders.data,
            'payforbalances': payforbalances.data
        }
    elif query == 'orders':
        paginator = PageNumberPagination()
        paginator.page_size = 12
        orders = Order.objects.filter(Q(summa__gt=0)).order_by('-date')
        order_page = paginator.paginate_queryset(orders, request)
        orders = OrderSerializer(
            order_page, many=True, context={'request': request})
        data = {
            "orders": orders.data
        }
    elif query == 'transactions':
        paginator = PageNumberPagination()
        paginator.page_size = 12
        transactions = PaymentHistory.objects.all().order_by('-date')
        transaction_page = paginator.paginate_queryset(transactions, request)
        transactions = PaymentHistorySerializer(
            transaction_page, many=True, context={'request': request})
        
        data = {
            "transactions": transactions.data,
        }
    elif query == 'payforbalances':
        paginator = PageNumberPagination()
        paginator.page_size = 12
        payforbalances = PayForBalance.objects.all().order_by('-date')
        payforbalance_page = paginator.paginate_queryset(payforbalances, request)
        payforbalances = PayForBalanceSerializer(payforbalance_page, many=True, context={'request': request})
        
        data = {
            'payforbalances': payforbalances.data
        }

    return paginator.get_paginated_response(data)
