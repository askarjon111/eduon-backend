from clickuz.views import ClickUzMerchantAPIView
from clickuz import ClickUz
from .models import OrderPayment


class OrderCheckAndPayment(ClickUz):
    def check_order(self, order_id: str, amount: str):
        try:
            order = OrderPayment.objects.get(id=int(order_id))
            if float(order.amount) == float(amount):
                order.status = 1
                return self.ORDER_FOUND
            else:
                order.status = 3
                return self.INVALID_AMOUNT
        except:
            return self.ORDER_NOT_FOUND

    def successfully_payment(self, order_id: str, transaction: object):
        order = OrderPayment.objects.get(id=int(order_id))
        user = order.user
        user.cash += order.amount
        user.save()
        order.status = 2
        order.save()


class TestView(ClickUzMerchantAPIView):
    VALIDATE_CLASS = OrderCheckAndPayment
