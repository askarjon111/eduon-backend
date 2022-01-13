from rest_framework import serializers

from home.models import Order
from uniredpay.models import PayForBalance


class PayForBalanceSerializers(serializers.ModelSerializer):
    class Meta:
        model = PayForBalance
        exclude = ['payment_id', 'uu_id']


class CourseOrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class UserSMSSerializers(serializers.Serializer):
    card_number = serializers.RegexField(regex=r'9860\d{12}|8600\d{12}')
    expire = serializers.CharField()
    amount = serializers.IntegerField(default=0)
    is_save = serializers.BooleanField(default=False)


class PayForBalanceSMSSerializer(serializers.Serializer):
    sms_code = serializers.CharField()


class PayForCourseWithoutSMSSerializer(serializers.Serializer):
    course_id = serializers.CharField()


class PayForCourseSMSSerializer(serializers.Serializer):
    sms_code = serializers.CharField()
    course_id = serializers.CharField()


class SpeakerCardSerializers(serializers.Serializer):
    card_number = serializers.RegexField(regex=r'9860\d{12}|8600\d{12}')
    expire = serializers.CharField()


class CardHistorySerializers(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
