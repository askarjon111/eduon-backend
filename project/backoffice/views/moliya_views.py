from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import Q
from backoffice.permissions import OwnerPermission, AdminPermission, ManagerPermission
from home.models import Order
from home.serializers import OrderSerializers
from paycom.models import Transaction
from paycom.serializers import TransactionSerializer


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission or AdminPermission or ManagerPermission])
def kirim_chiqim(request):
    transactions = Transaction.objects.all().order_by('time')
    orders = Order.objects.filter(Q(summa__gt=0)).order_by('-date')
    paginator = PageNumberPagination()
    paginator.page_size = 12
    transaction_page = paginator.paginate_queryset(transactions, request)
    order_page = paginator.paginate_queryset(orders, request)
    transactions = TransactionSerializer(
        transaction_page, many=True, context={'request': request})
    orders = OrderSerializers(
        order_page, many=True, context={'request': request})
    
    data = {
        "transactions": transactions.data,
        "orders": orders.data
    }
    
    return paginator.get_paginated_response(data)
