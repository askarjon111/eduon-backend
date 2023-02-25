from paycom.models import Transaction
from rest_framework import serializers


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        exclude = ["receivers", 'order_id']
