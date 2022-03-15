from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.PayForBalance)
admin.site.register(models.SpeakerTransaction)
# admin.site.register(models.UserSms)


@admin.register(models.PercentageOfSpeaker)
class PercentageModel(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        if models.PercentageOfSpeaker.objects.all():
            return False
        else:
            return True


@admin.register(models.PaymentHoldLimitTime)
class HoldModel(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        if models.PaymentHoldLimitTime.objects.all():
            return False
        else:
            return True
