import datetime
from home.models import *
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import Count, Q
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractHour, ExtractWeekDay
from backoffice.permissions import MarketingManagerPermission, OwnerPermission, ManagerPermission


# Spikerlar,  Foydalanuvchilar, Kurslar va buyurtmalar soni
@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission or MarketingManagerPermission or ManagerPermission])
def total_count(request):
    speakers = Speaker.objects.all().count()
    users = Users.objects.all().count()
    courses = Course.objects.all().count()
    orders = Order.objects.all().count()

    data = {
        "speakers": speakers,
        "users": users,
        "courses": courses,
        "orders": orders,

    }

    return JsonResponse(data)


# Kontent va auditoriya bo'limi
@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([MarketingManagerPermission or OwnerPermission or ManagerPermission])
def content_and_auditory(request):
    content = Course.objects.filter(
        date__year=datetime.datetime.now().year,
    ).annotate(
        month=ExtractMonth('date'),
    ).values(
        'month'
    ).annotate(
        content=Count('id')
    ).order_by('month')

    auditory = Users.objects.filter(
        regdate__year=datetime.datetime.now().year,
    ).annotate(
        month=ExtractMonth('regdate'),
    ).values(
        'month'
    ).annotate(
        auditory=Count('id')
    ).order_by('month')

    data = {
        "content": content,
        "auditory": auditory,
    }

    return Response(data)


# Foydalanuvchilar yoshi va jinsi
@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([MarketingManagerPermission or OwnerPermission or ManagerPermission])
def user_statistics(request):
    users = Users.objects.all()
    users1_17 = 0
    users18_23 = 0
    users24_29 = 0
    users30_35 = 0
    users36_45 = 0
    users46p = 0
    users_unknown = Users.objects.filter(Q(age=None)).count()
    age = [i.age.year for i in users if i.age is not None]
    for i in age:
        yosh = datetime.datetime.now().year - i
        if 1 <= yosh <= 17:
            users1_17 += 1
        elif 18 <= yosh <= 23:
            users18_23 += 1
        elif 24 <= yosh <= 29:
            users24_29 += 1
        elif 30 <= yosh <= 35:
            users30_35 += 1
        elif 36 <= yosh <= 45:
            users36_45 += 1
        elif yosh >= 46:
            users46p += 1
    male = Users.objects.filter(gender='erkak').count()
    if users.count() != 0:
        mpercent = (male / users.count()) * 100
        fpercent = 100 - mpercent
        data = {
            "age": {
                "u1_17": users1_17 / users.count() * 100,
                "u18_23": users18_23 / users.count() * 100,
                "u24_29": users24_29 / users.count() * 100,
                "u30_35": users30_35 / users.count() * 100,
                "u36_45": users36_45 / users.count() * 100,
                "u46p": users46p / users.count() * 100,
                "user_unknown": users_unknown,
            },
            "gender": {
                'yigitlar': mpercent,
                'qizlar': fpercent
            }
        }
    else:
        data = {
            "age": {
                "u1_17": 0,
                "u18_23": 0,
                "u24_29": 0,
                "u30_35": 0,
                "u36_45": 0,
                "u46p": 0,
                "user_unknown": users_unknown,
            },
            "gender": {
                'yigitlar': 0,
                'qizlar': 0
            }
        }

    return Response(data)


# Sotilgan kunlar: kecha, bugun, hafta, oy, yil uchun
@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission or MarketingManagerPermission or ManagerPermission])
def order_statistics(request):
    query = request.GET.get('query')
    if query == "hafta":
        weekly_statistics = Order.objects.filter(
            date__year=datetime.datetime.now().year,
            date__week=datetime.datetime.now().isocalendar()[1]).annotate(
            day=ExtractWeekDay('date'),
        ).values(
            'day'
        ).annotate(
            sells=Count('id')
        ).order_by('day')
        data = {
            "weekly_statistics": weekly_statistics,
        }
    elif query == "oy":
        monthly_statistics = Order.objects.filter(
            date__year=datetime.datetime.now().year,
            date__month=datetime.datetime.now().month
        ).annotate(
            day=ExtractDay('date'),
        ).values(
            'day'
        ).annotate(
            sells=Count('id')
        ).order_by('day')
        data = {
            "monthly_statistics": monthly_statistics,
        }
    elif query == "kecha":
        date = datetime.date.today() - datetime.timedelta(days=1)
        yesterday_statistics = Order.objects.filter(date__day=date.day).annotate(
            hour=ExtractHour('date'),
        ).values(
            'hour'
        ).annotate(
            sells=Count('id')
        ).order_by('hour')
        data = {
            "yesterday_statistics": yesterday_statistics,
        }
    elif query == "bugun":
        today_statistics = Order.objects.filter(date__day=datetime.datetime.now().day).annotate(
            hour=ExtractHour('date'),
        ).values(
            'hour'
        ).annotate(
            sells=Count('id')
        ).order_by('hour')
        data = {
            "today_statistics": today_statistics,
        }
    elif query == "yil":
        yearly_statistics = Order.objects.filter(
            date__year=datetime.datetime.now().year,
        ).annotate(
            month=ExtractMonth('date'),
        ).values(
            'month'
        ).annotate(
            sells=Count('id')
        ).order_by('month')
        data = {
            "yearly_statistics": yearly_statistics,
        }
    else:
        data = {
            "success": True,
            "message": "Noto'g'ri query",
        }
    return Response(data)


# Foydalanuvchilarning davlatlar bo'yicha statistikasi
@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([MarketingManagerPermission or OwnerPermission or ManagerPermission])
def country_statistics(request):
    users = Order.objects.all()
    cnt = 0
    country = {}
    uid = set()
    for i in users:
        if i.user_id not in uid:
            
            if i.user.country is None:
                ctry = "Noaniq"
            else:
                ctry = i.user.country.name
            uid.add(i.user_id)
            cnt += 1
            if ctry in country.keys():
                country[ctry] = country[ctry] + 1
            else:
                country[ctry] = 1
    for i in country.keys():
        country[i] = country[i] / cnt * 100
    data = {
        "country_statistics": country,
    }

    return Response(data)


@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def free_and_paid_courses(request):
    courses = Course.objects.all()
    paid = Course.objects.filter(turi='Pullik').count()
    if courses.count() != 0:
        paid = (paid / courses.count()) * 100
        free = 100 - paid

        data = {
            "paid_courses": paid,
            "free_courses": free,
        }
    else:
        data = {
            "paid_courses": 0,
            "free_courses": 0,
        }
    return Response(data)


# Kurslar foizi kategoriyalari bo'yicha
@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([MarketingManagerPermission or OwnerPermission or ManagerPermission])
def courses_by_categories(request):
    categories = CategoryVideo.objects.filter(parent=None)
    courses = Course.objects.all().count()
    data = {
        "success": "true",
    }
    for category in categories:
        category_courses = Course.objects.filter(
            Q(categories=category)).count()
        percent = (category_courses / courses) * 100
        data[f"{category}"] = percent

    return JsonResponse(data)
