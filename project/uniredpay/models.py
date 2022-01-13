from django.db import models

from home.models import Users, Course


class PercentageOfSpeaker(models.Model):
    from_own_staff = models.SmallIntegerField(default=90)
    from_user = models.SmallIntegerField(default=70)


class PayForBalance(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    tr_id = models.CharField(max_length=100, null=True, default=None, blank=True)
    date = models.DateTimeField(auto_now_add=True)


class UserSms(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    sms_code = models.PositiveIntegerField()
    card_number = models.CharField(max_length=20)
    card_expire = models.CharField(max_length=10)
    amount = models.PositiveIntegerField()


class PaymentHoldLimitTime(models.Model):
    day = models.PositiveSmallIntegerField(verbose_name='Kun', default=3)

    class Meta:
        verbose_name_plural = 'Foydalanuvchilarga to\'lovni qaytarish muddati'
