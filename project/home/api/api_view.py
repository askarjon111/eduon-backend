from rest_framework.pagination import PageNumberPagination
import datetime
from http.client import HTTPResponse
import random
from ratelimit.decorators import ratelimit

from clickuz import ClickUz
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractWeekDay

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import serializers


from home.models import (
    CourseModule, Users, PhoneCode, Country, Region, Course, Order, ContractWithSpeaker, CategoryVideo,
    Speaker, RankCourse, CommentCourse, OrderPayment, VideoCourse, File
)
from home.sms import sms_send
from home.serializers import CourseSerializer
from rest_framework_simplejwt.backends import TokenBackend
from simplejwt.tokens import RefreshToken
from .serializers import (
    BillingSerializer, OrderSerializer, UsersSerializer, CountrySerializer, RegionSerialzier, GetCourseSerializer, SpeakerGetSerializer, CategorySerializer,
    CourseDetailSerializer, BoughtedCourseSerializer, RatingSerializer, CommentSerializer, OrderPaymentSerializer,
    VideoSerializer

)
from ..serializers import CourseModuleSerializer, SpeakerModelSerializer, SpeakerCourseSerializer, UserSerializers, SpeakerSerializer, \
    VideoCourseSerializer


@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def speaker_orders(request):
    query = Order.objects.filter(course__author__speaker__id=request.user.id)
    orders = OrderSerializer(query, many=True)
    billings = BillingSerializer(query, many=True)
    data = {
        "success": True,
        "error": "",
        "orders": orders.data,
        "billings": billings.data
    }
    return Response(data)


def get_financial_statistics(request):
    speaker_money = Speaker.objects.aggregate(Sum('cash'))
    context = {
        'speaker_money': speaker_money['cash__sum']
    }

    return render(request, "admin/statistics.html", context)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def send_code(request):
    # was_limited = getattr(request, 'limited', False)
    # if was_limited:
    #     return JsonResponse({"code": 1, 'msg': 'try many times'},json_dumps_params={'ensure_ascii':False})
    # else:
    try:
        phone = request.GET.get('phone')
        type = request.GET.get('type')
        error = False
        code = random.randint(100000, 999999)
        stds = Users.objects.filter(phone=phone)
        sent_code = PhoneCode.objects.filter(
            phone=phone, created_at__gte=datetime.datetime.now() - datetime.timedelta(minutes=5)).count()
        if sent_code < 3:
            if stds.count() > 0:
                if type == "registeration":
                    error = True
            else:
                if type == "resset_password":
                    error = True

            if error == False:
                text = "Sizning tasdiq kodingiz {}. Eduon.uz".format(code)
                res = sms_send(phone, text)
                if res is not None:
                    p = PhoneCode.objects.create(phone=phone, code=code)

                    data = {
                        "success": True,
                        "message": "Code yuborildi!",
                    }
                else:
                    data = {
                        "success": False,
                        "message": "Code yuborilmadi!",
                    }
            else:
                if type == "registeration":
                    data = {
                        "success": False,
                        "message": "Bu telefon raqam oldin ro'yhatga olingan!",
                    }
                elif type == "resset_password":
                    data = {
                        "success": False,
                        "message": "Bu telefon raqam oldin ro'yhatga olinmagan!",
                    }
                else:
                    data = {
                        "success": False,
                        "message": "Qandaydur xatolik yuz berdi!",
                    }
        else:
            data = {
                "success": False,
                "message": "Urinishlar soni oshib ketdi, iltimos birozdan so'ng urinib ko'ring",
            }
    except Exception as er:
        data = {
            "success": False,
            "message": "{}".format(er),
        }

    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def verify_code(request):
    phone = request.GET.get('phone')
    code = request.GET.get('code')
    ph_c = PhoneCode.objects.filter(phone=phone, code=code)
    if ph_c.count() > 0:
        data = {
            "success": True,
            "error": "",
            "message": "Code Tasdiqlandi!",
            "data": {
                "phone": phone,
                "code": code
            }
        }
    else:
        data = {
            "success": False,
            "error": "",
            "message": "Code Tasdiqlanmadi!",
        }
    return Response(data)


@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def registeration(request):
    try:
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        phone = request.data.get("phone")
        password = request.data.get("password")
        gender = request.data.get("gender")
        code = request.data.get("code")
        ref_code = request.data.get("ref_code")
        ph_c = PhoneCode.objects.filter(phone=phone, code=code)
        if ph_c.count() > 0:
            std = Users.objects.create(
                phone=phone, first_name=first_name, last_name=last_name,
                gender=gender, password=password
            )
            try:
                usrs = Users.objects.get(own_ref_code=ref_code)
                std.bonus += 5000
                usrs.bonus += 5000
                usrs.save()
                std.save()
            except:
                pass
            ser = UsersSerializer(std)
            token = RefreshToken.for_user(std)
            tk = {
                "refresh": str(token),
                "access": str(token.access_token)
            }
            data = {
                "success": True,
                "error": "",
                "message": "Student yaratildi!",
                "data": {
                    "student": ser.data,
                    "token": tk
                }
            }
        else:
            data = {
                "success": False,
                "error": "Telefon raqam yoki tasdiq kodi xato!",
                "message": "",
            }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": "",
        }
    return Response(data)


@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def reset_password(request):
    try:
        phone = request.data.get('phone')
        password = request.data.get('password')
        code = request.data.get('code')
        ph_c = PhoneCode.objects.filter(phone=phone, code=code)
        if ph_c.count() > 0:
            try:
                student = Users.objects.get(phone=phone)
                student.password = make_password(password)
                student.save()
                data = {
                    "success": True,
                    "error": "",
                    "message": "Parol o'zgartirildi!",
                }
            except Users.DoesNotExist:
                data = {
                    "success": False,
                    "error": "Bunday foydalanuvchi mavjud emas!",
                    "message": "",
                }
        else:
            data = {
                "success": False,
                "error": "Tasdiqlash kodi xato!!",
                "message": "",
            }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": "",
        }

    return Response(data)


@api_view(['post'])
def set_photo(request):
    try:
        photo = request.FILES.get("photo")
        student = Users.objects.get(id=request.user.id)

        student.image = photo
        student.save()
        data = {
            "success": True,
            "error": "",
            "message": "Rasm o'zgartirildi!",
            "data": {
                "image": student.image.url
            }
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }
    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def get_countries(request):
    try:
        countries = Country.objects.all()
        ser = CountrySerializer(countries, many=True)
        data = {
            "success": True,
            "error": "",
            "message": "Mamlakatlar ma'lumoti olindi!",
            "data": ser.data
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }
    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def get_regions(request):
    try:
        regions = Region.objects.all()
        ser = RegionSerialzier(regions, many=True)
        data = {
            "success": True,
            "error": "",
            "message": "Viloyatlar ma'lumoti olindi!",
            "data": ser.data
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }
    return Response(data)


@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def full_registration(request):
    try:
        user = request.user
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        country = request.data.get("country")
        region = request.data.get("region")
        email = request.data.get("email")
        gender = request.data.get("gender")
        both_day = request.data.get("both_day")
        job = request.data.get("job")
        region_id = Region.objects.get(id=region)
        country_id = Country.objects.get(id=country)
        if user.first_name != first_name:
            user.first_name = first_name

        if user.last_name != last_name:
            user.last_name = last_name

        if user.country != country:
            user.country = country

        if user.region != region:
            user.region = region

        if user.email != email:
            user.email = email

        if user.gender != gender:
            user.gender = gender

        if user.age != both_day:
            user.age = both_day

        if user.job != job:
            user.job = job

        user.save()
        data = {
            "success": True,
            "error": "",
            "message": "Profil update qilindi!",
            "data": UsersSerializer(user).data
        }

    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }
    return Response(data)


@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def login(request):
    try:
        phone = request.data.get('phone')
        password = request.data.get('password')
        try:
            user = Users.objects.get(phone=phone)
            if check_password(password, user.password):
                ser = UsersSerializer(user)
                token = RefreshToken.for_user(user)
                tk = {
                    "refresh": str(token),
                    "access": str(token.access_token)
                }
                data = {
                    "success": True,
                    "error": "",
                    "message": "Kirish tasdiqlandi!",
                    "data": {
                        "student": ser.data,
                        "token": tk
                    }
                }
            else:
                data = {
                    "success": False,
                    "error": "Telefon raqam yoki password xato!!",
                    "message": ""
                }
                return JsonResponse(data, status=401)
        except Users.DoesNotExist:
            data = {
                "success": False,
                "error": "Bunday foydalanuvchi mavjud emas!",
                "message": ""
            }

    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }
    return Response(data)


@api_view(['post'])
def test(request):
    try:
        data = {
            "success": True,
            "error": "",
            "message": "Kurslar olindi!",
            "data": None
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def get_course(request):
    try:
        # category = request.GET.get('category')
        search = request.GET.get('q')
        if search is None:
            search = ""

        # if category is None:
        query = Course.objects.filter(
            name__icontains=search, is_confirmed=True)
        query2 = Speaker.objects.filter(Q(speaker__first_name__icontains=search) or Q(
            speaker__last_name__icontains=search))
        # else:
        #     query = Course.objects.filter(category_id=category, name__icontains=search)

        ser1 = GetCourseSerializer(query, many=True)
        ser2 = SpeakerGetSerializer(query2, many=True)
        data = {
            "success": True,
            "error": "",
            "message": "Kurslar olindi!",
            "data_courses": ser1.data,
            "data_speakers": ser2.data
        }

    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['get'])
def get_boughted_course(request):
    try:
        user = request.user
        orders = Order.objects.filter(user=user)
        courses = []
        for order in orders:
            ser = GetCourseSerializer(order.course)
            courses.append(ser.data)

        data = {
            "success": True,
            "error": "",
            "message": "Sotib olingan kurslar!",
            "data": courses
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['post'])
def buy_course(request):
    try:
        course = request.data['course']
        user = request.user
        cr = Course.objects.get(id=course)
        usr = Users.objects.get(id=int(user.id))
        eduonpay = ContractWithSpeaker.objects.last()
        if eduonpay is None:
            eduonpay = ContractWithSpeaker.objects.create(eduon=30)
        narxi = cr.price - cr.discount
        cash = usr.cash
        bonus = usr.bonus
        row = Order.objects.filter(course_id=course, user=user)
        if row.count() > 0:
            data = {
                "success": False,
                "error": "Bu kursni oldin sotib olgansiz!",
                "message": ""
            }
        else:
            if cash + bonus < narxi:
                data = {
                    "success": False,
                    "error": "Kursni sotib olish uchun hisobingizni to'ldiring!",
                    "message": ""
                }
            else:
                summa = narxi - bonus
                if summa > 0:
                    usr.cash = usr.cash + bonus - narxi
                    ord = Order.objects.create(course_id=course, user=user, summa=summa, bonus=bonus,
                                               discount=cr.discount)
                    usr.bonus = 0
                else:
                    usr.bonus = abs(summa)
                    ord = Order.objects.create(course_id=course, user=user, summa=0, bonus=narxi,
                                               discount=cr.discount)

                eduon_summa = eduonpay.eduon
                speaker = ord.course.author
                speaker.cash = int(
                    round(speaker.cash + ord.summa * (100 - eduon_summa) / 100))
                speaker.save()
                ord.sp_summa = int(
                    round(ord.summa * (100 - eduon_summa) / 100))
                ord.save()
                usr.save()
                data = {
                    "success": True,
                    "error": "",
                    "message": "Kurs sotib olindi!",
                }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def get_category(request):
    try:
        categories = CategoryVideo.objects.filter(parent=None)
        ser = CategorySerializer(categories, many=True)
        data = {
            "success": True,
            "error": "",
            "message": "Categoriyalar olindi!",
            "data": ser.data
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def course_detail(request):
    try:
        course_id = request.query_params.get("course_id", False)
        if course_id:
            course = Course.objects.get(id=course_id)
            ser = CourseDetailSerializer(course)
            data = {
                "success": True,
                "error": "",
                "message": "Kurs qabul qilindi!",
                "data": ser.data
            }
        else:
            data = {
                'success': False,
                'message': "?course_id={id} qilib id berish kerak"
            }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": "Kurs topilmadi"
        }

    return Response(data)


@api_view(['get'])
def boughted_course_detail(request):
    try:
        course_id = request.GET.get("course_id")
        user = request.user
        course = Course.objects.get(id=course_id)
        orders = Order.objects.filter(course_id=course_id, user=user)
        course = BoughtedCourseSerializer(course)
        if orders.count() > 0 or course.turi == "Bepul":

            data = {
                "success": True,
                "error": "",
                "message": "Kurslar olindi!",
                "course": course.data,
            }
        else:
            data = {
                "success": False,
                "error": "Bu Course sotib olinmagan",
                "message": ""
            }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def get_top_course(request):
    try:
        query = Course.objects.filter(is_top=1)
        ser = GetCourseSerializer(query, many=True)
        data = {
            "success": True,
            "error": "",
            "message": "Top Kurslar olindi!",
            "data": ser.data
        }

    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def get_speaker(request):
    try:
        type = request.GET.get('type')
        id = request.GET.get('id')
        if type == 'top':
            query = Speaker.objects.filter(is_top=1)
            ser = SpeakerGetSerializer(query, many=True)
        else:
            try:
                query = Speaker.objects.get(pk=id)
                ser = SpeakerGetSerializer(query)
            except:
                data = {
                    "success": False,
                    "error": 'Bunaqa speaker mavjud emas'
                }
                return JsonResponse(data, status=404)

        # if q is not None:
        #     search = str(q).split(" ")
        #     for d in search:
        #         query = query.filter(
        #             Q(speaker__first_name__icontains=d) |
        #             Q(speaker__last_name__icontains=d))
        data = {
            "success": True,
            "error": "",
            "message": "Speakerlar ro'yhati olindi!",
            "data": ser.data
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


def rating(cr, rn):
    value_sp = cr.aggregate(value=Sum('speaker_value')).get('value')
    if value_sp is None:
        value_sp = 0
    value_cr = cr.aggregate(value=Sum('course_value')).get('value')
    if value_cr is None:
        value_cr = 0

    value_tt = cr.aggregate(value=Sum('content_value')).get('value')
    if value_tt is None:
        value_tt = 0
    value_vt = cr.aggregate(value=Sum('video_value')).get('value')
    if value_vt is None:
        value_vt = 0

    count_cr = cr.filter(course_value__gt=0).count()
    if count_cr > 0:
        rank_cr = round(value_cr / count_cr, 2)
    else:
        rank_cr = 0
    count_sp = cr.filter(speaker_value__gt=0).count()
    if count_sp > 0:
        rank_sp = round(value_sp / count_sp, 2)
    else:
        rank_sp = 0
    count_tt = cr.filter(content_value__gt=0).count()
    if count_tt > 0:
        rank_tt = round(value_tt / count_tt, 2)
    else:
        rank_tt = 0
    count_vr = cr.filter(video_value__gt=0).count()
    if count_vr > 0:
        rank_vr = round(value_vt / count_vr, 2)
    else:
        rank_vr = 0

    data = {
        "course": {
            "rank": rank_cr,
            "count": count_cr
        },
        "speaker": {
            "rank": rank_sp,
            "count": count_sp
        },
        "content": {
            "rank": rank_tt,
            "count": count_tt
        },
        "video": {
            "rank": rank_vr,
            "count": count_vr
        }
    }
    ser = RatingSerializer(rn)
    data = {
        "rating_user": ser.data,
        "rating_full": data
    }
    return data


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def get_rating(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION', False)
        if token:
            access_token = token.split(' ')[-1]
            get_token = TokenBackend(algorithm='HS256').decode(
                access_token, verify=False)
            user = get_token.get('user_id')
            course_id = request.GET.get("course_id")
            print(course_id)
            speaker_courses = Course.objects.filter(
                author_id=Course.objects.get(id=course_id).author_id)
            speaker_courses_count = speaker_courses.count()
            ids = [i.id for i in speaker_courses]
            speaker_ranks = []
            for i in ids:
                try:
                    rnk = RankCourse.objects.get(course_id=i)
                except:
                    rnk = None
                    speaker_courses_count -= 1
                if rnk is not None:
                    course_rank = (rnk.course_value + rnk.video_value +
                                   rnk.content_value + rnk.speaker_value) / 4
                    speaker_ranks.append(course_rank)
            if speaker_courses_count != 0:
                speaker_rank = round(sum(speaker_ranks) /
                                     speaker_courses_count, 2)
            else:
                speaker_rank = 0
            try:
                rnk = RankCourse.objects.get(course_id=course_id)
                cr = RankCourse.objects.filter(course_id=course_id)
                data = {
                    "success": True,
                    "error": "",
                    "message": "Rating olindi!",
                    "speaker_rank": speaker_rank,
                    "data": rating(cr, rnk)
                }
            except RankCourse.DoesNotExist:
                data = {
                    "success": True,
                    "error": "",
                    "message": "Rating olindi!",
                    "speaker_rank": 0,
                    "data": {
                        "course": {
                            "rank": 0,
                            "count": 0
                        },
                        "speaker": {
                            "rank": 0,
                            "count": 0
                        },
                        "content": {
                            "rank": 0,
                            "count": 0
                        },
                        "video": {
                            "rank": 0,
                            "count": 0
                        }
                    }
                }
        else:
            data = {
                "success": False,
                "error": "Token yuborilmadi!"
            }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['post'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def set_rating(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION', False)
        if token:
            access_token = token.split(' ')[-1]
            get_token = TokenBackend(algorithm='HS256').decode(
                access_token, verify=False)
            user = get_token.get('user_id')
            course = request.POST.get('course_id')
            course_value = request.POST.get('course_value')
            speaker_value = request.POST.get('speaker_value')
            content_value = request.POST.get('content_value')
            video_value = request.POST.get('video_value')
            rnk = RankCourse.objects.filter(user_id=user, course_id=course)

            if rnk.count() > 0:
                rn = rnk.last()
                rn.course_value = course_value
                rn.speaker_value = speaker_value
                rn.content_value = content_value
                rn.video_value = video_value
                rn.save()
            else:
                rn = RankCourse.objects.create(
                    user_id=user, course_id=course, course_value=course_value,
                    speaker_value=speaker_value, content_value=content_value, video_value=video_value
                )
            cr = RankCourse.objects.filter(course_id=course)

            data = {
                "success": True,
                "error": "",
                "message": "You rated the course!",
                "data": rating(cr, rn)
            }
        else:
            data = {
                "success": False,
                "error": "Token yuborilmadi!"
            }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['post'])
def set_comment(request):
    try:
        user = request.user.id
        course = request.data.get('course_id')
        comment = request.data.get('comment')
        CommentCourse.objects.create(
            comment=comment, user_id=user, course_id=course)
        comments = CommentCourse.objects.filter(
            course_id=course).order_by('-id')
        ser = CommentSerializer(comments, many=True)
        data = {
            "success": True,
            "error": "",
            "message": "Comment qoldirildi!",
            "data": ser.data
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def get_comment(request):
    try:
        course_id = request.GET.get('course_id')
        comments = CommentCourse.objects.filter(
            course_id=course_id).order_by('-id')
        ser = CommentSerializer(comments, many=True)
        data = {
            "success": True,
            "error": "",
            "message": "Commentlar olindi!!",
            "data": ser.data
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['get'])
def create_invoise(request):
    try:
        amount = request.GET.get('amount')
        user = request.user
        order = OrderPayment.objects.create(
            type="Click",
            amount=amount,
            user=user
        )
        url = ClickUz.generate_url(order_id=str(order.id), amount=str(
            order.amount), return_url='https://eduon.uz')
        data = {
            "success": True,
            "error": "",
            "message": "Invoise yaratildi!",
            "data": url
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def create_invoise_payme(request):
    try:
        amount = int(request.query_params.get('amount')) * 100
        user = Users.objects.get(id=int(request.query_params.get('user_id')))

        order = OrderPayment.objects.create(
            type="PayMe",
            amount=amount,
            user=user
        )
        data = {
            "success": True,
            "error": "",
            "message": "Invoise yaratildi!",
            "data": {
                "order_id": order.id
            }
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['get'])
def payment_history(request):
    try:
        user = request.user
        date_start = request.GET.get("date_start")
        date_end = request.GET.get("date_end")
        orders = OrderPayment.objects.filter(
            user=user,
            date__gte=date_start,
            date__lte=date_end
        )
        ser = OrderPaymentSerializer(orders, many=True)
        data = {
            "success": True,
            "error": "",
            "message": "To'lovlar tarixi!",
            "data": ser.data
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def get_statistics(request):
    try:
        user = request.user
        sp = Speaker.objects.get(speaker_id=user.id)
        courses = Course.objects.filter(author_id=sp.id).count()
        users = Order.objects.filter(course__author_id=sp.id)
        course = Course.objects.filter(author_id=sp.id)
        cs = GetCourseSerializer(course, many=True)
        users1_17 = 0
        users18_23 = 0
        users24_29 = 0
        users30_35 = 0
        users36_45 = 0
        users46p = 0
        users_unknown = Order.objects.filter(
            Q(course__author_id=sp.id) and Q(user__age=None)).count()
        age = [i.user.age.year for i in users if i.user.age is not None]
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
        male = Order.objects.filter(
            Q(course__author_id=sp.id) and Q(user__gender='Erkak')).count()
        if users.count() != 0:
            mpercent = (male / users.count()) * 100
            fpercent = 100 - mpercent
            s = 0
            for i in range(len(cs.data)):
                s += cs.data[i]["sell_count"]
            data = {
                "success": True,
                "error": "",
                "message": "Statistika olindi!",
                "data": {
                    "course_count": courses,
                    "sell_count": s,
                    "cash": sp.cash,
                    "user_count": users.count(),
                    "u1_17": users1_17 / users.count() * 100,
                    "u18_23": users18_23 / users.count() * 100,
                    "u24_29": users24_29 / users.count() * 100,
                    "u30_35": users30_35 / users.count() * 100,
                    "u36_45": users36_45 / users.count() * 100,
                    "u46p": users46p / users.count() * 100,
                    "user_unknown": users_unknown,
                    "male": male,
                    'yigitlar': mpercent,
                    'qizlar': fpercent
                }
            }
        else:
            s = 0
            for i in range(len(cs.data)):
                s += cs.data[i]["sell_count"]
            data = {
                "success": True,
                "error": "",
                "message": "Statistika olindi!",
                "data": {
                    "course_count": courses,
                    "sell_count": s,
                    "cash": sp.cash,
                    "user_count": users.count(),
                    "u1_17": 0,
                    "u18_23": 0,
                    "u24_29": 0,
                    "u30_35": 0,
                    "u36_45": 0,
                    "u46p": 0,
                    'yigitlar': 0,
                    'qizlar': 0
                }
            }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }

    return Response(data)


@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def get_sell_course_statistics(request):
    try:
        query = request.GET.get('query')
        user = request.user
        sp = Speaker.objects.get(speaker_id=user.id)
        if query == "hafta":
            weekly_statistics = Order.objects.filter(course__author_id=sp.id).filter(
                date__year=datetime.datetime.now().year,
                date__week=datetime.datetime.now().isocalendar()[1]).annotate(
                day=ExtractWeekDay('date'),
            ).values(
                'day'
            ).annotate(
                sells=Count('id')
            ).order_by('day')
            data = {
                "success": True,
                "message": "",
                "data": {
                    "weekly_statistics": weekly_statistics,
                }
            }
        elif query == "oy":
            monthly_statistics = Order.objects.filter(course__author_id=sp.id).filter(
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
                "success": True,
                "message": "",
                "data": {
                    "monthly_statistics": monthly_statistics,
                }
            }
        elif query == "yil":
            yearly_statistics = Order.objects.filter(course__author_id=sp.id).filter(
                date__year=datetime.datetime.now().year,
            ).annotate(
                month=ExtractMonth('date'),
            ).values(
                'month'
            ).annotate(
                sells=Count('id')
            ).order_by('month')
            data = {
                "success": True,
                "message": "",
                "data": {
                    "yearly_statistics": yearly_statistics,
                }
            }
        else:
            data = {
                "success": True,
                "message": "Notugri query kelgan",
            }

    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }
    return Response(data)


@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def get_rank_statistics(request):
    try:
        query = request.GET.get('query')
        usr = request.user
        speaker = Speaker.objects.get(speaker=usr)
        if query == 'Video':
            cnt_1 = RankCourse.objects.filter(
                Q(video_value=1), Q(course__author_id=speaker.id)).count()
            cnt_2 = RankCourse.objects.filter(
                Q(video_value=2), Q(course__author_id=speaker.id)).count()
            cnt_3 = RankCourse.objects.filter(
                Q(video_value=3), Q(course__author_id=speaker.id)).count()
            cnt_4 = RankCourse.objects.filter(
                Q(video_value=4), Q(course__author_id=speaker.id)).count()
            cnt_5 = RankCourse.objects.filter(
                Q(video_value=5), Q(course__author_id=speaker.id)).count()
            add = cnt_1 + cnt_2 + cnt_3 + cnt_4 + cnt_5
            if add > 0:
                total = (cnt_1*1 + cnt_2*2 + cnt_3*3 + cnt_4*4 + cnt_5*5) / add
            else:
                total = 0
            data = {
                "success": True,
                "cnt_1": cnt_1,
                "cnt_2": cnt_2,
                "cnt_3": cnt_3,
                "cnt_4": cnt_4,
                "cnt_5": cnt_5,
                "total": total,
            }
        elif query == 'Kurs':
            cnt_1 = RankCourse.objects.filter(
                Q(course_value=1), Q(course__author=speaker.id)).count()
            cnt_2 = RankCourse.objects.filter(
                Q(course_value=2), Q(course__author=speaker.id)).count()
            cnt_3 = RankCourse.objects.filter(
                Q(course_value=3), Q(course__author=speaker.id)).count()
            cnt_4 = RankCourse.objects.filter(
                Q(course_value=4), Q(course__author=speaker.id)).count()
            cnt_5 = RankCourse.objects.filter(
                Q(course_value=5), Q(course__author=speaker.id)).count()
            add = cnt_1 + cnt_2 + cnt_3 + cnt_4 + cnt_5
            if add > 0:
                total =( cnt_1*1 + cnt_2*2 + cnt_3*3 + cnt_4*4 + cnt_5*5 )/ add
            else:
                total = 0
            data = {
                "success": True,
                "cnt_1": cnt_1,
                "cnt_2": cnt_2,
                "cnt_3": cnt_3,
                "cnt_4": cnt_4,
                "cnt_5": cnt_5,
                "total": total,
            }
        elif query == 'Kontent':
            cnt_1 = RankCourse.objects.filter(
                Q(content_value=1), Q(course__author=speaker.id)).count()
            cnt_2 = RankCourse.objects.filter(
                Q(content_value=2), Q(course__author=speaker.id)).count()
            cnt_3 = RankCourse.objects.filter(
                Q(content_value=3), Q(course__author=speaker.id)).count()
            cnt_4 = RankCourse.objects.filter(
                Q(content_value=4), Q(course__author=speaker.id)).count()
            cnt_5 = RankCourse.objects.filter(
                Q(content_value=5), Q(course__author=speaker.id)).count()
            add = cnt_1 + cnt_2 + cnt_3 + cnt_4 + cnt_5
            if add > 0:
                total =( cnt_1*1 + cnt_2*2 + cnt_3*3 + cnt_4*4 + cnt_5*5 )/ add
            else:
                total = 0
            data = {
                "success": True,
                "cnt_1": cnt_1,
                "cnt_2": cnt_2,
                "cnt_3": cnt_3,
                "cnt_4": cnt_4,
                "cnt_5": cnt_5,
                "total": total,
            }
        elif query == 'Spiker':
            cnt_1 = RankCourse.objects.filter(
                Q(speaker_value=1), Q(course__author=speaker.id)).count()
            cnt_2 = RankCourse.objects.filter(
                Q(speaker_value=2), Q(course__author=speaker.id)).count()
            cnt_3 = RankCourse.objects.filter(
                Q(speaker_value=3), Q(course__author=speaker.id)).count()
            cnt_4 = RankCourse.objects.filter(
                Q(speaker_value=4), Q(course__author=speaker.id)).count()
            cnt_5 = RankCourse.objects.filter(
                Q(speaker_value=5), Q(course__author=speaker.id)).count()
            add = cnt_1 + cnt_2 + cnt_3 + cnt_4 + cnt_5
            if add > 0:
                total =( cnt_1*1 + cnt_2*2 + cnt_3*3 + cnt_4*4 + cnt_5*5 )/ add
            else:
                total = 0
            data = {
                "success": True,
                "cnt_1": cnt_1,
                "cnt_2": cnt_2,
                "cnt_3": cnt_3,
                "cnt_4": cnt_4,
                "cnt_5": cnt_5,
                "total": total,
            }
        elif query == 'Umumiy':
            speaker_course_ranks = RankCourse.objects.filter(
                course__author=speaker.id)
            cnt_1 = 0
            cnt_2 = 0
            cnt_3 = 0
            cnt_4 = 0
            cnt_5 = 0
            for i in speaker_course_ranks:
                cnt = (i.video_value + i.course_value +
                       i.content_value + i.speaker_value) / 4
                if 1 <= cnt <= 1.5:
                    cnt_1 += 1
                elif 1.5 < cnt <= 2.5:
                    cnt_2 += 1
                elif 2.5 < cnt <= 3.5:
                    cnt_3 += 1
                elif 3.5 < cnt <= 4.5:
                    cnt_4 += 1
                elif 4.5 < cnt <= 5:
                    cnt_5 += 1
            add = cnt_1 + cnt_2 + cnt_3 + cnt_4 + cnt_5
            if add > 0:
                total =( cnt_1*1 + cnt_2*2 + cnt_3*3 + cnt_4*4 + cnt_5*5 )/ add
            else:
                total = 0
            data = {
                "success": True,
                "cnt_1": cnt_1,
                "cnt_2": cnt_2,
                "cnt_3": cnt_3,
                "cnt_4": cnt_4,
                "cnt_5": cnt_5,
                "total": total,
            }
        else:
            data = {
                "success": True,
                "message": "Noto'gri query yuborilgan",
            }
    except Exception as e:
        data = {
            "success": False,
            "error": "{}".format(e),
            "message": ""
        }
    return Response(data)


@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def content_and_auditory(request):
    user = request.user
    sp = Speaker.objects.get(speaker_id=user.id)
    content = Course.objects.filter(Q(author_id=sp) &
                                    Q(date__year=datetime.datetime.now().year),
                                    ).annotate(
        month=ExtractMonth('date'),
    ).values(
        'month'
    ).annotate(
        content=Count('id')
    ).order_by('month')
    auditory = Order.objects.filter(Q(course__author_id=sp.id) & Q(user__regdate__year=datetime.datetime.now().year),
    ).annotate(
        month=ExtractMonth('user__regdate'),
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


@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def get_user_country_statistics(request):
    try:
        user = request.user
        sp = Speaker.objects.get(speaker_id=user.id)
        users = Order.objects.filter(
            Q(course__author_id=sp.id) & Q(user__country__id__gte=0))
        cnt = 0
        country = {}
        uid = set()
        for i in users:
            if i.user_id not in uid:
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
            "success": True,
            "message": "",
            "data": {
                "country_statistic": country,
            }
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }
    return Response(data)


@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def get_user_region_statistics(request):
    try:
        user = request.user
        sp = Speaker.objects.get(speaker_id=user.id)
        users = Order.objects.filter(
            Q(course__author_id=sp.id) & Q(user__region__id__gte=0))
        cnt = 0
        region = {}
        uid = set()
        for i in users:
            if i.user_id not in uid:
                reg = i.user.region.name
                uid.add(i.user_id)
                cnt += 1
                if reg in region.keys():
                    region[reg] = region[reg] + 1
                else:
                    region[reg] = 1
        for i in region.keys():
            region[i] = region[i] / cnt * 100
        data = {
            "success": True,
            "message": "",
            "data": {
                "region_statistic": region,
            }
        }
    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }
    return Response(data)


@api_view(['post'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def upload_file(request):
    try:
        user = request.user
        sp = Speaker.objects.get(speaker_id=user.id)
        name = request.POST.get('name')
        # try:
        #     courseModule = request.POST.get('courseModule')
        # except:
        #     courseModule = None

        # try:
        #     place_number = request.POST.get('place_number')
        # except:
        #     place_number = None

        try:
            file = request.FILES.get('file')
        except:
            file = None
        if file is not None and name != '':
            new = File.objects.create(
                speaker_id=sp.id,
                name=name,
                file=file,
                # courseModule=courseModule,
                # place_numer=place_number,
            )
            new.save()
            data = {
                'success': True,
                'message': 'Fayl yuklandi',
                'path': new.file.path
            }
        else:
            data = {
                'success': False,
                'message': 'Fayl yuklanmadi'
            }
            return JsonResponse(data, status=405)
    except:
        data = {
            'success': False,
            'message': 'Xatolik!'
        }
        return JsonResponse(data, status=405)
    return JsonResponse(data, status=200)


@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def get_speaker_data(request):
    try:
        us = request.user
        speaker = Speaker.objects.get(speaker_id=us.id)
        cr = Course.objects.filter(author_id=speaker.id)
        video = VideoCourse.objects.filter(author_id=speaker.id)
        sp = UserSerializers(us)
        srr = CourseSerializer(cr, many=True)
        videos = VideoCourseSerializer(video, many=True)
        data = {
            'speaker': sp.data,
            'courses': srr.data,
            'videos': videos.data
        }
    except:
        data = {
            'success': False,
            'message': 'Xatolik!'
        }
    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def get_speaker_courses(request):
    try:
        id = request.GET.get('id')
        paginator = PageNumberPagination()
        paginator.page_size = 12
        course_objects = Course.objects.filter(author_id=id)
        courses = paginator.paginate_queryset(course_objects, request)
        sr = GetCourseSerializer(courses, many=True)
        data = sr.data
    except Exception as e:
        data = {
            "success": False,
            "message": "{}".format(e)
        }
        return JsonResponse(data, status=405)
    return paginator.get_paginated_response(data)


def verified_courses(request):
    try:
        courses = Course.objects.filter(is_confirmed=True).count()
        data = {
            "success": True,
            "count": courses
        }
    except:
        data = {
            "success": False,
            "error": "Xatolik!!!"
        }
        return JsonResponse(data, status=405)
    return JsonResponse(data, status=200)


def verified_speaker_courses(request):
    try:
        speaker_count = Course.objects.filter(
            is_confirmed=True).distinct().count()
        data = {
            "success": True,
            "speaker_count": speaker_count
        }
    except:
        data = {
            "success": False,
            "error": "Xatolik!!!"
        }
    return JsonResponse(data, status=200)


@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def get_courses(request):
    try:
        user = request.user
        sp = Speaker.objects.get(speaker_id=user.id)
        cs = Course.objects.filter(author_id=sp.id)
        courses = CourseSerializer(cs, many=True)
        vd = VideoCourse.objects.filter(author_id=sp.id)
        videos = VideoSerializer(vd, many=True)

        data = {
            "success": True,
            "courses": courses.data,
            "videos": videos.data
        }
    except:
        data = {
            "success": False,
            "message": "Xatolik!!!"
        }
        return JsonResponse(data, status=405)
    return Response(data)
