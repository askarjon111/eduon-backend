from rest_framework import serializers
from home.api.serializers import FileSerializer, LanguageSerializer, SpeakerGetSerializer, VideoSerializer
from home.models import Admin, Course, CourseModule, File, ForWhomCourse, Order, RankCourse, ReferalValue, RequirementsCourse, Speaker, Users, VideoCourse, WhatYouLearn, PaymentHistory
from django.db.models import Count, Q, Sum
from paycom.models import Transaction
from home.serializers import CountrySerializer, CourseModuleSerializer, CourseTagsSerializer, CourseTrailerSerializer, DjangoUserSerializers, ForWhomCourseSerializer, RequirementsCourseSerializer, WhatYouLearnSerializer
from quiz.models import Quiz
from quiz.serializers import QuizSerializer
from uniredpay.models import PayForBalance


class OrderSerializer(serializers.ModelSerializer):
    user = DjangoUserSerializers(read_only=True)
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        type = 'order'
        return type

    class Meta:
        model = Order
        fields = "__all__"


class PaymentHistorySerializer(serializers.ModelSerializer):
    user = DjangoUserSerializers(read_only=True)
    type = serializers.SerializerMethodField()
    
    def get_type(self, obj):
        type = 'transaction'
        return type

    class Meta:
        model = PaymentHistory
        fields = '__all__'


class AdminLoginSerializer(serializers.ModelSerializer):
    admin = DjangoUserSerializers()
    
    class Meta:
        model = Admin
        fields = '__all__'

class ReferalValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferalValue
        fields = '__all__'

class SpeakerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    orders = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    eduons_revenue = serializers.SerializerMethodField()
    transactions = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    def get_name(self, obj):
        first_name = obj.speaker.first_name
        last_name = obj.speaker.last_name
        return f"{first_name} {last_name}"
    
    
    def get_email(self, obj):
        email = obj.speaker.email
        return email
    
    
    def get_orders(self, obj):
        orders = Order.objects.filter(course__author=obj.id)
        return orders.count()
    

    def get_courses(self, obj):
        courses = Course.objects.filter(author=obj.id)
        return courses.count()

    def get_students(self, obj):
        students = Order.objects.filter(course__author_id=obj.id).values_list('user', flat=True).distinct()
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
        fields = ['id', 'name', 'both_date', 'kasbi', 'phone', 'email', 'country', 'city', 'compony', 'card_number', 'cash', 'courses',
                  'students', 'rating', 'revenue', 'eduons_revenue', 'transactions',  'image', 'orders']


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
    user = DjangoUserSerializers(read_only=True)
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        type = 'payforbalance'
        return type

    class Meta:
        model = PayForBalance
        fields = ['user', 'amount', 'date', 'type']     


class CourseListSerializer(serializers.ModelSerializer):
    course_rank = serializers.SerializerMethodField()
    sell_count = serializers.SerializerMethodField()
    author_image = serializers.SerializerMethodField()

    def get_author_image(self, obj):
        author_image = obj.author.image.url
        return author_image

    def get_course_rank(self, obj):
        cr = RankCourse.objects.filter(course_id=obj.id)
        value = cr.aggregate(value=Sum('course_value')).get('value')
        count = cr.filter(course_value__gt=0).count()
        if value is None:
            value = 0
        if count > 0:
            return {"rank": round(value / count, 2), "count": count}
        else:
            return {"rank": 0, "count": 0}

    def get_sell_count(self, obj):
        try:
            sells = Order.objects.filter(course_id=obj.id)
            return sells.count()
        except:
            return 0
    class Meta:
        model = Course
        fields = ['id', 'name', 'image', 'author_image',
                  'price', 'view', 'course_rank', 'sell_count']


class CourseDetailSerializer(serializers.ModelSerializer):
    from home.serializers import CategorySerializer
    modules = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    author = SpeakerGetSerializer(read_only=True)
    sell_count = serializers.SerializerMethodField()
    course_rank = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    quizzes = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True)
    language = LanguageSerializer()
    trailer = CourseTrailerSerializer()
    whatyoulearns = serializers.SerializerMethodField()
    requirementscourse = serializers.SerializerMethodField()
    forwhoms = serializers.SerializerMethodField()
    course_tags = CourseTagsSerializer(many=True)

    def get_requirementscourse(self, obj):
        try:
            requirementscourse = RequirementsCourse.objects.filter(
                course=obj)
            return RequirementsCourseSerializer(requirementscourse, many=True).data
        except:
            return None

    def get_forwhoms(self, obj):
        try:
            forwhoms = ForWhomCourse.objects.filter(
                course=obj)
            return ForWhomCourseSerializer(forwhoms, many=True).data
        except:
            return None

    def get_whatyoulearns(self, obj):
        try:
            whatyoulearns = WhatYouLearn.objects.filter(
                course=obj)
            return WhatYouLearnSerializer(whatyoulearns, many=True).data
        except:
            return None

    def get_course_rank(self, obj):
        cr = RankCourse.objects.filter(course_id=obj.id)
        value = cr.aggregate(value=Sum('course_value')).get('value')
        count = cr.filter(course_value__gt=0).count()
        if value is None:
            value = 0
        if count > 0:
            return {"rank": round(value / count, 2), "count": count}
        else:
            return {"rank": 0, "count": 0}

    def get_sell_count(self, obj):
        try:
            sells = Order.objects.filter(course_id=obj.id)
            return sells.count()
        except:
            return 0

    def get_videos(self, obj):
        try:
            videos = VideoCourse.objects.filter(course=obj)
            return VideoSerializer(videos, many=True).data
        except:
            return None

    def get_quizzes(self, obj):
        try:
            quizzes = Quiz.objects.filter(
                module__course=obj)
            return QuizSerializer(quizzes, many=True).data
        except:
            return None

    def get_modules(self, obj):
        try:
            modules = CourseModule.objects.filter(
                course=obj).order_by("place_number")
            return CourseModuleSerializer(modules, many=True).data
        except:
            return None

    def get_files(self, obj):
        try:
            files = File.objects.filter(courseModule__course=obj)
            return FileSerializer(files, many=True).data
        except:
            return None

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "image",
            "turi",
            "author",
            "level",
            "language",
            "price",
            "categories",
            "date",
            "upload_or_youtube",
            "description",
            "discount",
            "view",
            "is_top",
            "is_tavsiya",
            "trailer",
            "videos",
            "course_rank",
            "sell_count",
            "modules",
            "files",
            "quizzes",
            "requirementscourse",
            "whatyoulearns",
            "forwhoms",
            "course_tags",
        ]