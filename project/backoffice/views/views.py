import datetime

import requests as sender
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from backoffice.serializers import AdminLoginSerializer
from simplejwt.tokens import RefreshToken
import random
import string
from home.sms import sms_send
from ratelimit.decorators import ratelimit
from eduon import settings
from home.models import *
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.contrib.auth.models import Group
from backoffice.permissions import OwnerPermission, AdminPermission, ManagerPermission


@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def AdminLoginView(request):
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            admin = Admin.objects.get(admin__username=username)
            user = User.objects.get(username=username)
            roles = []
            groups = Group.objects.filter(user=user)
            for group in groups:
                roles.append(group.name)

            if check_password(password, user.password):
                ser = AdminLoginSerializer(admin)
                token = RefreshToken.for_user(admin.admin)
                tk = {
                    "refresh": str(token),
                    "access": str(token.access_token)
                }
                data = {
                    "success": True,
                    "error": "",
                    "message": "Kirish tasdiqlandi!",
                    "data": {
                        "admin": {
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'username': user.username,
                            'email': user.email,
                            'roles': roles
                        },
                        "token": tk,
                        
                    }
                }
            else:
                data = {
                    "success": False,
                    "error": "Telefon raqam yoki password xato!!",
                    "message": ""
                }
        except Admin.DoesNotExist:
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


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([OwnerPermission | AdminPermission | ManagerPermission])
def eduon_revenue(request):
    speaker_cash = Speaker.objects.filter(cash__gt=0).aggregate(Sum('cash'))
    user_cash = Users.objects.filter(cash__gt=0).aggregate(Sum('cash'))
    wallets = wallet_api(data={}, method='wallet.balance')
    wallet_balance = str(wallets['result']['balance'])
    if speaker_cash['cash__sum'] is None:
        with_users_cash = wallet_balance
    else:
        with_users_cash = int(wallet_balance) / 100 - speaker_cash['cash__sum']

    if user_cash['cash__sum'] is None:
        eduon_revenue = with_users_cash
    else:
<<<<<<< HEAD
        eduon_revenue = with_users_cash - user_cash['cash__sum']

=======
        user_cash = str(user_cash['cash__sum'])
git
            eduon_revenue = with_users_cash - int(user_cash[:-2])
        else:
            eduon_revenue = with_users_cash
  
>>>>>>> server

    data = {
        "speaker_cash": speaker_cash,
        "user_cash": user_cash,
        "eduon_revenue": eduon_revenue,
    }
    return JsonResponse(data)


def users_cash_to_bonus(request):
    users = Users.objects.filter(cash__gt=0)
    for user in users:
        user.bonus += user.cash
        user.cash = 0
        user.save()
        
    return HttpResponse('ok')


def PagenatorPage(List, num, request):
    paginator = Paginator(List, num)
    pages = request.GET.get('page')

    try:
        list = paginator.page(pages)
    except PageNotAnInteger:
        list = paginator.page(1)
    except EmptyPage:
        list = paginator.page(paginator.num_pages)
    return list


# backofficeni userlarini rollarga bo'lish
def switcher(user, success_status):
    try:
        admin = Admin.objects.get(admin=user)
    except:
        admin = None

    if admin is None:
        return redirect('page-404')

    statuslar = admin.status.all()
    status = []
    for st in statuslar:
        status.append(st.status)

    if 1 in status or success_status in status:
        return None
    elif 2 in status:
        return redirect('backoffice-speaker')
    elif 3 in status:
        return redirect('backoffice-users')
    elif 4 in status:
        return redirect('backoffice-course')
    elif 5 in status:
        return redirect('moliya')
    elif 6 in status:
        return redirect('tasdiq')
    elif 7 in status:
        return redirect('backoffice-tolov')
    elif 8 in status:
        return redirect('sozlamalar')
    elif 9 in status:
        return redirect('backoffice-home')
    else:
        return redirect('page-404')


# Backofficedagi moliya bo'limi
@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def moliya(request):
    param = request.query_params.get("filter")
    if param == "sotuv":
        jami_summa = OrderPayment.objects.aggregate(total=Sum('amount')).get("total")

        context = {
            "jami_summa": jami_summa,
        }
    return JsonResponse(context)


# backofficegi speaker bo'limi
class SpeakerDetail(LoginRequiredMixin, DetailView):
    template_name = 'backoffice/speaker-detail.html'
    model = Speaker

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        ad = Admin.objects.filter(admin_id=user.id).count()
        if ad <= 0:
            return redirect('page-404')
        else:
            res = switcher(user, 2)
            if res is not None:
                return res
        return super(SpeakerDetail, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SpeakerDetail, self).get_context_data(**kwargs)
        cource_count = Course.objects.filter(author=self.object)
        sel_count = Order.objects.filter(course__author=self.object)
        context['course_count'] = cource_count.count()
        context['sell_count'] = sel_count.count()
        return context


# backofficedagi sozlamalar bo'limi
class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'backoffice/settings.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        ad = Admin.objects.filter(admin_id=user.id).count()
        if ad <= 0:
            return redirect('page-404')
        else:
            res = switcher(user, 8)
            if res is not None:
                return res
        return super(SettingsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        super(SettingsView, self).get_context_data(**kwargs)
        ref = ReferalValue.objects.last()
        reg_bonus = RegBonus.objects.last()
        if reg_bonus is None:
            reg_bonus = RegBonus.objects.create(summa_full=0, summa=0)
        if ref is None:
            ref_sp = 0
            ref_us = 0
        else:
            ref_sp = ref.speaker_value
            ref_us = ref.user_value
        context = {
            "foiz": ContractWithSpeaker.objects.last(),
            "ref_sp": ref_sp,
            "ref_us": ref_us,
            "reg_bonus": reg_bonus
        }
        return context


# kusrlar sotuvidan eduon oladigon foizni belgilash bo'limi
def setContrantWithSpeaker(request):
    foiz = request.POST.get('foiz')
    if foiz is not None:
        ct = ContractWithSpeaker.objects.last()
        if ct is None:
            ct = ContractWithSpeaker.objects.create(eduon=foiz)
        else:
            ct.eduon = foiz
            ct.save()
        return redirect('sozlamalar')
    else:
        return redirect('sozlamalar')


# referallar orqali kelgan speakerlar uchun bonus miqdorini belgilash
def setReferalValueSp(request):
    value = request.POST.get('value')
    if value is not None:
        ct = ReferalValue.objects.last()
        if ct is None:
            ct = ReferalValue.objects.create(speaker_value=value)
        else:
            ct.speaker_value = value
            ct.save()
        return redirect('sozlamalar')
    else:
        return redirect('sozlamalar')


# ro'yhatdan o'tganda beriladigon bonus miqdorini belgilash
def setBonusSumma(request):
    summa = request.POST.get("reg_summa")
    summa_full = request.POST.get("reg_summa_full")
    reg_bonus = RegBonus.objects.last()
    if summa is not None:
        reg_bonus.summa = summa

    if summa_full is not None:
        reg_bonus.summa_full = summa_full

    reg_bonus.save()
    return redirect('sozlamalar')


# referallar orqali kelgan userlar uchun bonus miqdorini belgilash
def setReferalValueUS(request):
    value = request.POST.get('value')
    if value is not None:
        ct = ReferalValue.objects.last()
        if ct is None:
            ct = ReferalValue.objects.create(user_value=value)
        else:
            ct.user_value = value
            ct.save()
        return redirect('sozlamalar')
    else:
        return redirect('sozlamalar')


# speakerlarni tasdiqlash
@login_required(login_url='login')
def TasdiqOk(request):
    delete = request.GET.get('delete')
    accept = request.GET.get('accept')
    if delete is not None:
        sp = Speaker.objects.get(id=delete)
        user = sp.speaker
        user.delete()
        sms_send(sp.phone, settings.SMS_REJECT_TEXT)
        # result = sender.get(settings.SMS_BASE_URL + '/api/message/sms/send',
        #                     {'mobile_phone': sp.phone, 'message': settings.SMS_REJECT_TEXT},
        #                     headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'}).json()
    elif accept is not None:
        sp = Speaker.objects.get(id=accept)
        sp.status = 2
        sp.save()
        print("ACTIVATION SMS SEND!")
        sms_send(sp.phone, settings.SMS_ACCEPT_TEXT)
        # result = sender.post(settings.SMS_BASE_URL + '/api/message/sms/send',
        #                      {'mobile_phone': sp.phone, 'message': settings.SMS_ACCEPT_TEXT},
        #                      headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'}).json()
    return redirect('tasdiq')


# to'lovni accespt qilish
def accespt_billing(request):
    id = request.GET.get('id')
    bil = Billing.objects.get(id=id)
    sp = bil.speaker
    bil.summa = sp.cash
    bil.status = 1
    bil.save()
    sp.cash = 0
    sp.save()
    sms_send(sp.phone, "Eduon.uz saytidan hisobingizga {} so'm yuborildi.".format(bil.summa))
    # result = sender.post(settings.SMS_BASE_URL + '/api/message/sms/send',
    #                      {'mobile_phone': sp.phone.replace("+", ""),
    #                       'message': "Eduon.uz saytidan hisobingizga {} so'm yuborildi.".format(bil.summa)},
    #                      headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'}).json()
    # print(result)
    return redirect('backoffice-tolov')


# to'lov accountlarini olish
def get_billings_count(request):
    billings = Billing.objects.filter(status=0)
    data = {
        "count": billings.count()
    }
    return JsonResponse(data)


# to'lovni bekor qilish
def cancel_billing(request):
    id = request.GET.get('id')
    bil = Billing.objects.get(id=id)
    bil.status = 2
    bil.save()
    return redirect('backoffice-tolov')


# tasdiq bo'limi
class TasdiqView(LoginRequiredMixin, TemplateView):
    template_name = 'backoffice/tasdiq.html'
    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        ad = Admin.objects.filter(admin_id=user.id).count()
        if ad <= 0:
            return redirect('page-404')
        else:
            res = switcher(user, 6)
            if res is not None:
                return res
        return super(TasdiqView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        super(TasdiqView, self).get_context_data(**kwargs)
        # tasdiqs = Speaker.objects.filter(status=1)
        context = {
            # 'tasdiqs': tasdiqs,
            'not_confirmed_courses': Course.objects.filter(is_confirmed=False)
        }
        return context


# to'lov bo'limi
class Tolov(LoginRequiredMixin, TemplateView):
    template_name = 'backoffice/tolov.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        ad = Admin.objects.filter(admin_id=user.id).count()
        if ad <= 0:
            return redirect('page-404')
        else:
            res = switcher(user, 7)
            if res is not None:
                return res
        return super(Tolov, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        super(Tolov, self).get_context_data(**kwargs)
        billings = Billing.objects.filter(status=0)
        context = {
            "billings": billings
        }
        return context


@login_required(login_url='login')
def CountOfferAjax(request):
    tasdiqs = Course.objects.filter(is_confirmed=False)
    billings = Billing.objects.filter(status=0)
    data = {
        'count': tasdiqs.count(),
        'bil_count': billings.count()
    }
    return JsonResponse(data)


# dashbord bo'limi
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'backoffice/home.html'

    # login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        r = sender.patch(settings.SMS_BASE_URL + '/api/auth/refresh',
                         headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'}).json()
        settings.SMS_TOKEN = r['data']['token']
        try:
            rs = sender.post(settings.SMS_BASE_URL_GLOBAL + '/oauth/token',
                             {'client_id': settings.SMS_CLIENT_ID, 'secret': settings.SMS_SECRET_KEY_GLOBAL,
                              "expires_in": 3600}).json()
            settings.SMS_TOKEN_GLOBAL = rs['jwt']
        except:
            pass
        user = request.user
        ad = Admin.objects.filter(admin_id=user.id).count()
        if ad <= 0:

            from django.http import Http404
            raise Http404()
            # return render(request, 'base/page-404.html', status=404)
        else:
            res = switcher(user, 9)
            if res is not None:
                return res
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        super(HomeView, self).get_context_data(**kwargs)
        speakers = Speaker.objects.all()
        users = Users.objects.all()
        courses = Course.objects.all()
        orders = Order.objects.all()

        context = {
            'speaker_count': speakers.count(),
            'user_count': users.count(),
            'order_count': orders.count(),
            'course_count': courses.count(),
        }
        return context


# chegirma belgilash
def set_discount(request):
    print(request.GET)
    summa = request.GET.get('summa')
    print(summa)
    id = request.GET.get('id')
    cr = Course.objects.get(id=id)
    cr.discount = summa
    cr.save()
    return JsonResponse({}, safe=False)


# speakerlar bo'limi
class SpeakersView(LoginRequiredMixin, TemplateView):
    template_name = 'backoffice/speaker.html'
    login_url = '/login'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        ad = Admin.objects.filter(admin_id=user.id).count()
        if ad <= 0:
            return redirect('page-404')
        else:
            res = switcher(user, 2)
            if res is not None:
                return res
        return super(SpeakersView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        super(SpeakersView, self).get_context_data(**kwargs)

        speakers = Speaker.objects.filter(status=2).extra(
            select={
                'rating': 'SELECT SUM(value) FROM home_rank WHERE home_rank.speaker_id=home_speaker.id',
                'count': 'SELECT COUNT(id) FROM home_rank WHERE home_rank.speaker_id=home_speaker.id',
                'course': 'SELECT COUNT(id) FROM home_course WHERE home_course.author_id=home_speaker.id',
                'sells': 'SELECT COUNT(id) FROM home_order WHERE home_order.course_id in (SELECT id FROM home_course '
                         'WHERE home_course.author_id=home_speaker.id)'
            },
        )
        try:
            q = self.request.GET['q']
            sp = speakers.filter(speaker__first_name__icontains=q)
        except:
            sp = speakers.order_by('-id')
        speaker_list = sp
        context = {
            'speakers': PagenatorPage(speaker_list, 8, self.request)
        }
        return context


# speakerlar kurslarini olish
@login_required(login_url='login')
def SpeakerCourse(request):
    user = request.user
    ad = Admin.objects.filter(admin_id=user.id).count()
    if ad <= 0:
        return redirect('page-404')
    else:
        res = switcher(user, 4)
        if res is not None:
            return res

    speaker = request.GET.get('speaker')
    courses = Course.objects.filter(author_id=speaker).extra(
        select={
            'sells': 'select count(id) from home_order where home_order.course_id=home_course.id and home_course.author_id={}'.format(
                speaker),
            'videos': 'select count(id) from home_videocourse where home_videocourse.course_id=home_course.id'
        },
    )
    context = {
        'courses': courses,
    }
    return render(request, 'backoffice/speaker-course.html', context)


# kurslar statusini o'zgartirish
def ChangeCourseStatus(request):
    id = request.GET['id']
    cr = Course.objects.get(id=id)

    if request.GET.get('is_top', False):
        is_top = request.GET['is_top']
        cr.is_top = is_top

    if request.GET.get('confirm', False):
        confirm_val = request.GET.get('confirm')

        if confirm_val in [1, True, '1', 'True', 'true', 'yes']:
            cr.is_confirmed = True
        elif confirm_val in [0, False, '0', 'False', 'false', 'no']:
            cr.is_confirmed = False

    cr.save()
    return JsonResponse({})


# Kurslarni tavsilar ro'yhatiga qo'shish
def ChangeCourseStatusTavsiya(request):
    id = request.GET['id']
    is_top = request.GET['is_tavsiya']
    cr = Course.objects.get(id=id)
    cr.is_tavsiya = is_top
    cr.save()
    try:
        tv = EduonTafsiyasi.objects.get(course_id=id)
        if is_top == '0':
            tv.delete()
    except EduonTafsiyasi.DoesNotExist:
        if is_top == '1':
            EduonTafsiyasi.objects.create(course_id=id)
    except EduonTafsiyasi.MultipleObjectsReturned:
        tv = EduonTafsiyasi.objects.filter(course_id=id)
        tv.delete()
        if is_top == '1':
            EduonTafsiyasi.objects.create(course_id=id)
    except Exception as err:
        print(err)
    return JsonResponse({})


# speakerlar statusini o'zgartirish yani top speakerlar qatoriga qo'shish
def ChangeSpeakerStatus(request):
    id = request.GET['id']
    is_top = request.GET['is_top']
    cr = Speaker.objects.get(id=id)
    cr.is_top = is_top
    cr.save()
    return JsonResponse({})


def ChangeCashUser(request):
    if request.POST.get('id', False) and request.POST.get('cash', False):
        id = request.POST.get('id', False)

        if request.user.is_authenticated and request.user in request.user.admin_set.all() and int(
                id) == request.user.id:
            cash = request.POST['cash']
            cr = Users.objects.get(id=id)
            cr.cash = cr.cash + int(cash)
            cr.save()
            data = {
                'cash': cr.cash
            }
            return JsonResponse(data)
        else:
            return JsonResponse({})
    else:
        return JsonResponse({})


def ChangeBonusUser(request):
    if request.POST.get('id', False) and request.POST.get('cash', False):
        id = request.POST.get('id', False)

        if request.user.is_authenticated and request.user in request.user.admin_set.all() and int(
                id) == request.user.id:
            cash = request.POST['cash']
            cr = Users.objects.get(id=id)
            cr.bonus = cr.bonus + int(cash)
            cr.save()
            data = {
                'bonus': cr.bonus
            }
            return JsonResponse(data)
        else:
            return JsonResponse({})
    else:
        return JsonResponse({})


@login_required(login_url='login')
def CoursesView(request):
    user = request.user
    ad = Admin.objects.filter(admin_id=user.id).count()
    if ad <= 0:
        return redirect('page-404')

    courses = Course.objects.extra(
        select={
            'sells': 'select count(id) from home_order where home_order.course_id=home_course.id',
            'videos': 'select count(id) from home_videocourse where home_videocourse.course_id=home_course.id'
        },
    )
    try:
        q = request.GET['q']
        cour = courses.filter(name__icontains=q)
    except:
        cour = courses
    context = {
        'courses': PagenatorPage(cour, 20, request),
    }
    return render(request, 'backoffice/course.html', context)


@login_required(login_url='login')
def Foydalanuvchilar(request):
    user = request.user
    ad = Admin.objects.filter(admin_id=user.id).count()
    if ad <= 0:
        return redirect('page-404')
    else:
        res = switcher(user, 3)
        if res is not None:
            return res

    users = Users.objects.extra(
        select={
            'sells': 'select count(id) from home_order where home_order.user_id=home_users.id'
        }
    )
    try:
        q = request.GET['q']
        foydal = users.filter(Q(first_name__icontains=q) | Q(phone__icontains=q))
    except:
        foydal = users
    context = {
        'users': PagenatorPage(foydal, 20, request),
    }
    return render(request, 'backoffice/users.html', context)


@login_required(login_url='login')
def AjaxCharts(request):
    pullik_course = Course.objects.filter(turi='Pullik').count()
    bepul_course = Course.objects.filter(turi='Bepul').count()
    sotilgan = ['SotilganKurslar', ]
    speaker = ['Speakerlar', ]
    foydal = ['Foydalanuvchilar', ]
    kurs = ['Kurslar', ]
    videos = ['Videolar', ]
    date = datetime.datetime.today()
    year = date.year
    for i in range(1, 13):
        st = Order.objects.filter(date__month=i, date__year=year).count()
        sp = Speaker.objects.filter(speaker__date_joined__month=i, speaker__date_joined__year=year).count()
        foyd = Users.objects.filter(regdate__month=i, regdate__year=year).count()
        kur = Course.objects.filter(date__month=i, date__year=year).count()
        vid = VideoCourse.objects.filter(date__month=i, date__year=year).count()

        sotilgan.append(st)
        speaker.append(sp)
        foydal.append(foyd)
        kurs.append(kur)
        videos.append(vid)
    combine = [sotilgan, speaker, foydal, kurs, videos]
    yoshdata = [
        [15, 20],
        [21, 30],
        [31, 40],
        [41, 0]
    ]
    yosh = []
    for ysh in yoshdata:
        sana_s = str((year - ysh[1])) + "-01-01"
        sana_e = str((year - ysh[0])) + "-12-31"
        if ysh[1] == 0:
            yosh1520 = Users.objects.filter(age__lte=sana_e).count()
        else:
            yosh1520 = Users.objects.filter(age__gte=sana_s, age__lte=sana_e).count()
        dt = [str(ysh[0]) + "-" + str(ysh[1]), yosh1520]
        yosh.append(dt)

    cat = []
    row = []
    category = CategoryVideo.objects.all()[0:5]
    viloyatlar = Region.objects.all()
    viloyat = []
    foydalanuvchi = ['Foydalanuvchi', ]
    for vil in viloyatlar:
        viloyat.append(vil.name)
        count = Users.objects.filter(region=vil).count()
        foydalanuvchi.append(count)

    for ct in category:
        course = Course.objects.filter(category_id=ct.id).count()
        row.append(ct.name)
        row.append(course)
        cat.append(row)
        row = []
    data = {
        'pullik_course': pullik_course,
        'bepul_course': bepul_course,
        'combine': combine,
        'yosh': yosh,
        'cat': cat,
        'foydalanuvchi': foydalanuvchi,
        'viloyat': viloyat,
    }
    return JsonResponse(data)


@ratelimit(key='ip', rate='2/m')
def check_phone_number(request):
    phone_number = request.POST.get('phone')
    if phone_number:
        if Speaker.objects.filter(phone=phone_number).exists():
            return JsonResponse({'status': "This number already registered!"})

        # result = sender.get(settings.SMS_BASE_URL + '/api/auth/user',
        #                     headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'}).json()
        # print(result)
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        sms_send(phone_number, settings.SMS_REGISTER_TEXT + code)
        # result = sender.post(settings.SMS_BASE_URL + '/api/message/sms/send',
        #                      {'mobile_phone': phone_number, 'message': settings.SMS_REGISTER_TEXT + code},
        #                      headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'}).json()
        try:
            usr = User.objects.get(username=phone_number)
            usr.password = code
            usr.save()
        except User.DoesNotExist:
            User.objects.create(
                username=phone_number,
                email=phone_number,
                password=code
            )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


@ratelimit(key='ip', rate='2/m')
def check_phone_number_reset(request):
    phone_number = request.POST.get('phone')
    if phone_number:
        if Speaker.objects.filter(phone=phone_number).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            sms_send(phone_number, settings.SMS_REGISTER_TEXT + code)
            # result = sender.post(settings.SMS_BASE_URL + '/api/message/sms/send',
            #                      {'mobile_phone': phone_number, 'message': settings.SMS_REGISTER_TEXT + code},
            #                      headers={'Authorization': f'Bearer {settings.SMS_TOKEN}'}).json()
            try:
                usr = User.objects.get(username=phone_number)
                usr.password = code
                usr.save()
            except User.DoesNotExist:
                pass
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})
