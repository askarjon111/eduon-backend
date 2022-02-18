from rest_framework import serializers
from home.models import Admin, Course, Order, RankCourse, Speaker, Users
from django.db.models import Count, Q, Sum
from paycom.models import Transaction
from home.serializers import CountrySerializer, DjangoUserSerializers
from uniredpay.models import PayForBalance


class AdminLoginSerializer(serializers.ModelSerializer):
    admin = DjangoUserSerializers()
    
    class Meta:
        model = Admin
        fields = '__all__'



class SpeakerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    eduons_revenue = serializers.SerializerMethodField()
    transactions = serializers.SerializerMethodField()

    def get_name(self, obj):
        first_name = obj.speaker.first_name
        last_name = obj.speaker.last_name
        return f"{first_name} {last_name}"

    def get_courses(self, obj):
        courses = Course.objects.filter(author=obj.id)
        return courses.count()

    def get_students(self, obj):
        students = Order.objects.filter(course__author_id=obj.id)
        return students.count()

    def get_rating(self, obj):
        cr = RankCourse.objects.filter(course__author=obj.id)
        count = cr.filter(speaker_value__gt=0).count()
        value = cr.aggregate(value=Sum('speaker_value')).get('value')
        if value is None:
            value = 0
        if count > 0:
            return {"rank": round(value / count, 2), "count": count}
        else:
            return {"rank": 0, "count": 0}

    def get_revenue(self, obj):
        revenue = Order.objects.filter(
            course__author=obj.id).aggregate(revenue=Sum('sp_summa'))
        return revenue.get('revenue')

    def get_eduons_revenue(self, obj):
        revenue = Order.objects.filter(
            course__author=obj.id).aggregate(revenue=Sum('for_eduon'))
        return revenue.get('revenue')

    def get_transactions(self, obj):
        transactions = Transaction.objects.filter(
            receivers=obj.card_number).aggregate(transactions=Sum('amount'))

        return transactions.get('transactions')

    class Meta:
        model = Speaker
        fields = ['id', 'name', 'both_date', 'kasbi', 'phone', 'country', 'city', 'compony', 'card_number', 'cash', 'courses',
                  'students', 'rating', 'revenue', 'eduons_revenue', 'transactions',  'image']


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    country = CountrySerializer()
    pay_for_balances = serializers.SerializerMethodField()
    total_bonus = serializers.SerializerMethodField()
    used_bonus = serializers.SerializerMethodField()
    total_balance = serializers.SerializerMethodField()
    used_money = serializers.SerializerMethodField()

    def get_name(self, obj):
        first_name = obj.first_name
        last_name = obj.last_name
        return f"{first_name} {last_name}"

    def get_courses(self, obj):
        courses = Order.objects.filter(user=obj.id)
        return courses.count()

    def get_pay_for_balances(self, obj):
        pay_for_balances = PayForBalance.objects.filter(user=obj.id).count()
        
        return pay_for_balances
    
    def get_total_balance(self, obj):
        total_balance = PayForBalance.objects.filter(user=obj.id).aggregate(total_balance=Sum('amount'))

        return total_balance.get('total_balance')
    
    def get_used_money(self, obj):
        used_money = PayForBalance.objects.filter(
            user=obj.id).aggregate(used_money=Sum('amount') - obj.cash)

        return used_money.get('used_money')
    
    def get_total_bonus(self, obj):
        total_bonus = Order.objects.filter(user=obj.id).aggregate(total_bonus=Sum('bonus')+ obj.bonus)
        return total_bonus.get('total_bonus')
    
    def get_used_bonus(self, obj):
        used_bonus = Order.objects.filter(user=obj.id).aggregate(used_bonus=Sum('bonus'))
        return used_bonus.get('used_bonus')
    
    class Meta:
        model = Users
        fields = ['id', 'name', 'age', 'job', 'phone',
                  'country', 'region', 'total_balance', 'used_money', 'cash', 'courses', 'image', 'bonus', 'pay_for_balances', 'total_bonus', 'used_bonus']

class PayForBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayForBalance
        fields = ['id', 'amount', 'date']