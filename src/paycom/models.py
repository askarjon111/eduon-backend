from django.db import models
from .utils import time_now_in_ms
from .exceptions import PaycomException


# Create your models here.

class Transaction(models.Model):
    TIMEOUT_LIMIT = 43200000

    STATE_CREATED = 1
    STATE_PAYED = 2
    STATE_CANCELLED = -1
    STATE_CANCELLED_AFTER_PAYED = -2

    REASON_USER_NOT_FOUND_ERROR = 1
    REASON_DEBIT_OPERATION_ERROR = 2
    REASON_EXECUTION_ERROR = 3
    REASON_TIMEOUT_CANCEL_ERROR = 4
    REASON_REFUND = 5
    REASON_UNDEFINED_ERROR = 6

    # paycom transaction id
    transaction_id = models.CharField(max_length=25, blank=False)
    # paycom transaction time
    time = models.CharField(max_length=13, blank=False)

    amount = models.IntegerField(blank=False)
    account = models.CharField(blank=False, max_length=255)

    create_time = models.FloatField(blank=True, default=0)
    perform_time = models.FloatField(blank=True, default=0)
    cancel_time = models.FloatField(blank=True, default=0)

    # transaction = models.CharField(blank=False, max_length=25)
    state = models.SmallIntegerField(blank=False)
    reason = models.SmallIntegerField(blank=True, default=0)
    receivers = models.CharField(max_length=500, blank=True, null=True)
    order_id = models.IntegerField(blank=False)

    def is_created(self):
        return self.state == self.STATE_CREATED

    def is_payed(self):
        return self.state == self.STATE_PAYED

    def is_cancelled(self):
        return self.state == self.STATE_CANCELLED

    def is_cancelled_after_payment(self):
        return self.state == self.STATE_CANCELLED_AFTER_PAYED

    def is_timeout(self):
        return time_now_in_ms() - int(self.time)*1000 > self.TIMEOUT_LIMIT

    def set_timed_out(self):
        self.reason = self.REASON_TIMEOUT_CANCEL_ERROR
        self.state = self.STATE_CANCELLED
        return self.save()

    def cancel(self, reason):
        if self.is_payed():
            self.state = self.STATE_CANCELLED_AFTER_PAYED
        elif self.is_created():
            self.state = self.STATE_CANCELLED
        self.cancel_time = time_now_in_ms()
        self.reason = reason
        return self.save()

    def set_payed(self):
        self.state = Transaction.STATE_PAYED
        self.perform_time = time_now_in_ms()
        self.save()

    @classmethod
    def between(cls, from_date, to_date):
        return Transaction.objects.filter(create_time__gte=from_date, create_time__lte=to_date)

    @staticmethod
    def find_by_pk(pk):
        try:
            transaction = Transaction.objects.get(transaction_id=pk)
            return transaction
        except Transaction.DoesNotExist as e:
            raise PaycomException("TRANSACTION_NOT_FOUND")
