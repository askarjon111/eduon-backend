import csv
import datetime
import os
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import HttpResponseRedirect, redirect, render
from django.views.generic import DetailView, TemplateView
from eduon.settings import BASE_DIR
from rest_framework_simplejwt import tokens
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import ListCreateAPIView
from django_filters.rest_framework import DjangoFilterBackend


from home.serializers import (SpeakerLoginSerializer, SpeakerSerializer, CourseSerializer)

from .models import *
from .serializers import DjangoUserSerializers, GetSpeakerSerializer


class CourseListCreateView(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    authentication_classes = []
    permission_classes = []
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    
    filterset_fields = ['categories']
    


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


def Page404(request, exception):
    return render(request, 'base/page-404.html', status=404)


# videolarni o'chirish
def deleteVideo(request):
    id = request.POST['id']
    vd = VideoCourse.objects.filter(id=id)
    vd.delete()
    return redirect('speaker-courses')


# info bo'limi
class InfoView(LoginRequiredMixin, TemplateView):
    template_name = 'speaker/info.html'
    login_url = 'login/'

    def dispatch(self, request, *args, **kwargs):
        # if chekUser(request):
        #     return chekUser(request)
        chekedUser = chekUser(request)
        if chekedUser:
            return chekedUser
        return super(InfoView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        super(InfoView, self).get_context_data(**kwargs)
        info = Info.objects.first()
        infoContents = InfoWidget.objects.all()
        service = ServiceInfo.objects.first()
        context = {
            'infos': info,
            'wigets': infoContents,
            'inf': 'active',
            'service': service,
            'user': self.request.user
        }
        return context


# video haqidagi malumotlar
class VideoDetail(LoginRequiredMixin, DetailView):
    template_name = 'speaker/video-play.html'
    login_url = '/login'
    model = VideoCourse
    context_object_name = 'video'

    def dispatch(self, request, *args, **kwargs):
        # if chekUser(request):
        #     return chekUser(request)
        chekedUser = chekUser(request)
        if chekedUser:
            return chekedUser
        return super(VideoDetail, self).dispatch(request, *args, **kwargs)


# video yuklash bo'limi
class VideoUpload(LoginRequiredMixin, TemplateView):
    template_name = 'speaker/upload-video.html'
    login_url = '/login'

    def dispatch(self, request, *args, **kwargs):
        # if chekUser(request):
        #     return chekUser(request)
        chekedUser = chekUser(request)
        if chekedUser:
            return chekedUser
        return super(VideoUpload, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        super(VideoUpload, self).get_context_data(**kwargs)
        user = self.request.user
        speaker = Speaker.objects.get(speaker_id=user.id)
        courses_pullik = Course.objects.filter(author_id=speaker.id, turi="Pullik")
        courses_bepul = Course.objects.filter(author_id=speaker.id, turi="Bepul")
        context = {
            'courses_pullik': courses_pullik,
            'courses_bepul': courses_bepul,
            'vd': 'active'
        }
        return context


# to'lov bo'limi
class BillingView(LoginRequiredMixin, TemplateView):
    template_name = 'speaker/billing.html'

    def get_context_data(self, **kwargs):
        super(BillingView, self).get_context_data(**kwargs)
        speaker = Speaker.objects.get(speaker=self.request.user)
        billing_query = Billing.objects.filter(speaker=speaker).order_by('-id')
        summa = billing_query.filter(status=1).aggregate(total=Sum('summa')).get('total')
        date = self.request.GET.get('date')
        course_id = self.request.GET.get('course')
        if summa is None:
            summa = 0

        if course_id is not None and date is not None:
            if course_id == "0" and date != "":
                month = date.split("-")[1]
                year = date.split("-")[0]
                orders = Order.objects.filter(course__author=speaker, date__month=month, date__year=year).order_by(
                    '-id')
            elif course_id != "0" and date != "":
                month = date.split("-")[1]
                year = date.split("-")[0]
                orders = Order.objects.filter(course__author=speaker, course_id=course_id, date__month=month,
                                              date__year=year).order_by('-id')
            elif course_id != "0" and date == "":
                orders = Order.objects.filter(course__author=speaker, course_id=course_id).order_by('-id')
            else:
                orders = Order.objects.filter(course__author=speaker).order_by('-id')
        else:
            orders = Order.objects.filter(course__author=speaker).order_by('-id')
        sp_summa_total = orders.aggregate(total=Sum('sp_summa')).get('total')
        if sp_summa_total is None:
            sp_summa_total = 0
        courses = Course.objects.filter(author=speaker)
        context = {
            'balans': speaker.cash,
            "bl": "active",
            "bil_last": billing_query.first(),
            "billings": PagenatorPage(billing_query, 10, self.request),
            "summa": summa,
            "orders": PagenatorPage(orders, 10, self.request),
            "sp_summa": sp_summa_total,
            "courses": courses
        }
        return context


# speakerlar kurslari
class CourseSpeaker(LoginRequiredMixin, TemplateView):
    template_name = 'speaker/course.html'
    login_url = '/login'

    def dispatch(self, request, *args, **kwargs):
        # if chekUser(request):
        #     return chekUser(request)
        chekedUser = chekUser(request)
        if chekedUser:
            return chekedUser
        user = request.user
        speaker = Speaker.objects.get(speaker_id=user.id)
        try:
            txt = speaker.image.url
        except Exception:
            txt = None

        if user.first_name == '' or user.last_name == '' or txt is None or speaker.description == '':
            print('ok')
            messages.info(request, "Iltimos shaxsiy malumotlaringizni to'ldiring!")
            return redirect('profile')
        return super(CourseSpeaker, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        super(CourseSpeaker, self).get_context_data()
        categories = CategoryVideo.objects.all()
        user = self.request.user
        speaker = Speaker.objects.get(speaker_id=user.id)
        rnk = Rank.objects.filter(speaker=speaker)
        value = rnk.aggregate(total=Sum('value')).get('total')
        if value is None:
            rank = 0.0
        else:
            rank = value / rnk.count()

        courses = Course.objects.filter(author_id=speaker.id).order_by('-id')
        kurslar = []
        for course in courses:
            videos = VideoCourse.objects.filter(course_id=course.id)
            viewcount = videos.aggregate(total=Sum('views_count')).get('total')
            if viewcount is None:
                viewcount = 0
            sell_count = Order.objects.filter(course_id=course.id).count()
            try:
                logo = course.author.logo
            except:
                logo = None

            try:
                img = course.image.url
            except:
                img = None

            dt = {
                'name': course.name,
                'price': round(course.price / 1000, 2),
                'price2': course.price,
                'category': course.category.name,
                'image': img,
                'video_or_url': course.upload_or_youtube,
                'description': course.description,
                'id': course.id,
                'discount': course.discount,
                'count': videos.count(),
                'sell_count': sell_count,
                'date': str(course.date),
                'views': viewcount,
                'logo': logo,
                'rank': rank,
                'rankmass': [1, 2, 3, 4, 5],
                'is_confirmed': course.is_confirmed,
            }
            kurslar.append(dt)
        context = {
            'categories': categories,
            'courses': kurslar,
            'cr': 'active',
        }
        return context


# videolar4 bo'limi
class VideosView(LoginRequiredMixin, TemplateView):
    template_name = 'speaker/videos.html'
    login_url = '/login'

    def get_context_data(self, **kwargs):
        super(VideosView, self).get_context_data(**kwargs)
        course = self.request.GET.get('course')
        course_obj = Course.objects.get(id=course)
        if course_obj.upload_or_youtube == "Video":
            status = '1'
        else:
            status = '0'
        course_data = {
            'id': course_obj.id,
            'name': course_obj.name,
            "status": status
        }
        try:
            videos = VideoCourse.objects.filter(course_id=course).order_by("place_number")
            videolar = []
            for video in videos:
                likes = LikeOrDislike.objects.filter(value=1, video_id=video.id).count()
                dislikes = LikeOrDislike.objects.filter(value=-1, video_id=video.id).count()
                views = VideoViews.objects.filter(video_id=video.id).count()

                dt = {
                    'likes': likes,
                    'dislikes': dislikes,
                    'views': views,
                    'video': video
                }
                videolar.append(dt)
            context = {
                'videolar': videolar,
                'vd': 'active',
                'course_obj': course_data

            }

        except Exception:
            context = {
                'count_video': 0,
                'videos': [],
                'vd': 'active',
                'course_obj': course_data

            }

        return context


# dashbord
class HomeSpeaker(LoginRequiredMixin, TemplateView):
    template_name = 'speaker/home.html'
    login_url = '/login'

    def dispatch(self, request, *args, **kwargs):
        # Original
        # if chekUser(request):
        #     return chekUser(request)

        chekedUser = chekUser(request)

        if chekedUser:
            return chekedUser
        return super(HomeSpeaker, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        super(HomeSpeaker, self).get_context_data(**kwargs)
        user = self.request.user
        try:
            speaker = Speaker.objects.get(speaker_id=user.id)
        except Speaker.DoesNotExist as err:
            return redirect('logout')

        course_count = Course.objects.filter(author_id=speaker.id).count()
        rank = Rank.objects.filter(speaker_id=speaker.id)
        sell_count = Order.objects.filter(course__author_id=speaker.id).count()
        reyting = rank.aggregate(total_summa=Sum('value')).get('total_summa')
        orders = Order.objects.filter(course__author_id=speaker.id).order_by('-id')[0:50]
        if reyting is None:
            reyting = 0
        try:
            rnk = reyting / rank.count()
        except ZeroDivisionError:
            rnk = 0
        context = {
            'course_count': course_count,
            'hm': 'active',
            'rank': rnk,
            'sells': sell_count,
            'orders': orders
        }

        return context


# profil bo'limi
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'speaker/profile.html'
    login_url = '/login'

    def dispatch(self, request, *args, **kwargs):
        # if chekUser(request):
        #     return chekUser(request)
        chekedUser = chekUser(request)
        if chekedUser:
            return chekedUser
        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        super(ProfileView, self).get_context_data(**kwargs)
        user = self.request.user
        try:
            speaker = Speaker.objects.get(speaker_id=user.id)
        except Speaker.DoesNotExist as err:
            return redirect('logout')

        course_count = Course.objects.filter(author_id=speaker.id).count()
        rank = RankCourse.objects.filter(course__author_id=speaker.id, speaker_value__gt=0)
        sell_count = Order.objects.filter(course__author_id=speaker.id).count()
        reyting = rank.aggregate(total_summa=Sum('speaker_value')).get('total_summa')
        if reyting is None:
            reyting = 0
        try:
            rnk = reyting / rank.count()
        except ZeroDivisionError:
            rnk = 0
        context = {
            'course_count': course_count,
            'speaker': speaker,
            'rank': rnk,
            'sells': sell_count,
        }

        return context


# speakerlar ro'yhatini xls ga export qilish
@login_required(login_url='login')
def export_speaker(request):
    us = request.user
    admins = Admin.objects.filter(admin=us)
    if admins.count() == 0:
        return redirect('speaker-home')
    response = HttpResponse(
        content_type='text/csv',
    )
    response['Content-Disposition'] = "attachment; filename=speaker.csv"
    writer = csv.writer(response)
    writer.writerow([
        "Ism", "Familya", "Telefon", "Kompaniya",
        "Kasbi", "Xabar", "Tug'ilgan sana", "Mamlakat", "Viloyat"
    ])
    speakers = Speaker.objects.all()
    for sp in speakers:
        writer.writerow([
            sp.speaker.first_name, sp.speaker.last_name, sp.phone,
            sp.kasbi, sp.message, sp.both_date, sp.country, sp.city
        ]
        )
    return response


# userlar ro'yhatini xls ga export qilish
@login_required(login_url='login')
def export_user(request):
    us = request.user
    admins = Admin.objects.filter(admin=us)
    if admins.count() == 0:
        return redirect('speaker-home')
    response = HttpResponse(
        content_type='text/csv',
    )
    response['Content-Disposition'] = "attachment; filename=user.csv"
    writer = csv.writer(response)
    writer.writerow([
        "Ism", "Familya", "Telefon",
        "Kasbi", "Tug'ilgan sana", "Mamlakat", "Viloyat"
    ])
    users = Users.objects.all()
    for user in users:
        if user.country is not None:
            cn = user.country.name
        else:
            cn = ""
        if user.region is not None:
            rg = user.region.name
        else:
            rg = ""

        writer.writerow([
            user.first_name, user.last_name, user.phone,
            user.job, user.age, cn, rg
        ]
        )
    return response


# video yuklash
@login_required(login_url='login')
def UploadVideoPost(request):
    if chekUser(request):
        return chekUser(request)
    if request.method == 'POST':
        url = ''
        title = request.POST['title']
        course = request.POST['kurs']
        rasm = request.FILES['image']
        link = request.POST['url']
        place_number = request.POST['place_number']
        if link != '':
            a = link.split('watch?v=')
            url = "https://www.youtube.com/embed/" + a[1][:11]
        video = request.FILES.get('video', None)
        desc = request.POST['desc']
        user = request.user
        speaker = Speaker.objects.get(speaker_id=user.id)
        VideoCourse.objects.create(title=title, course_id=course, image=rasm, video=video,
                                   url=url, description=desc, author_id=speaker.id, place_number=place_number)
        return redirect('speaker-courses')


# document yuklash
def upload_document(request):
    if request.method == "POST":
        title = request.POST['title']
        rasm = request.FILES['rasm']
        desc = request.POST['desc']
        dockument = request.FILES['dockument']
        place_number = request.POST['place_number']
        course = request.POST['course']
        user = request.user
        speaker = Speaker.objects.get(speaker_id=user.id)
        VideoCourse.objects.create(title=title, is_file=True, course_id=course, image=rasm, video=dockument,
                                   description=desc, author_id=speaker.id, place_number=place_number)
        return redirect('speaker-courses')


# documentni tahrirlash
def edit_document(request):
    print(request.POST)
    if request.method == "POST":
        title = request.POST['title_edit']
        rasm = request.FILES.get('rasm')
        desc = request.POST['desc']
        dockument = request.FILES.get('dockument')
        place_number = request.POST['place_number_edit']
        course = request.POST['course']
        id = request.POST['doc_id']
        video = VideoCourse.objects.get(id=id)
        if title != "":
            video.title = title
        if rasm is not None and rasm != "":
            video.image = rasm
        if dockument is not None and dockument != "":
            video.video = dockument

        if desc != "":
            video.description = desc

        if place_number != "":
            video.place_number = place_number

        video.save()
        return redirect('speaker-courses')


# videoni tahrirlash
@login_required(login_url='login')
def EditVideoPost(request):
    if chekUser(request):
        return chekUser(request)
    if request.method == 'POST':
        url = ''
        title = request.POST['title_edit']
        course = request.POST['kurs_edit']
        rasm = request.FILES.get('image_edit', None)
        link = request.POST['url_edit']
        id = request.POST['id']
        place_number = request.POST['place_number_edit']
        try:
            if link != '':
                a = link.split('watch?v=')
                url = "https://www.youtube.com/embed/" + a[1][:11]
        except:
            pass
        video = request.FILES.get('video_edit', None)
        desc = request.POST['desc_edit']
        vid = VideoCourse.objects.get(id=id)
        if course != "":
            vid.course_id = course
        if title != "":
            vid.title = title
        if rasm != "" and rasm is not None:
            vid.image = rasm
        if video != "" and video is not None:
            vid.video = video
        if place_number != "":
            vid.place_number = place_number
        if url != "":
            vid.url = url
        if desc != "":
            vid.description = desc
        vid.save()
        return redirect('speaker-courses')


# videolarni olish
def get_video(request):
    id = request.GET.get('id')
    video = VideoCourse.objects.get(id=id)
    data = {
        "id": video.id,
        "name": video.title,
        "url": video.url,
        "place_number": video.place_number,
        "desc": video.description
    }
    return JsonResponse(data)


# videoni o'chirish
@login_required(login_url='login')
def VideoDelete(request):
    if chekUser(request):
        return chekUser(request)
    if request.method == 'POST':
        id = request.POST['id']
        video_course = VideoCourse.objects.get(id=id)
        video_course.delete()
        # title = request.POST['title']
        # course = request.POST['kurs']
        # rasm = request.FILES['image']
        # video = request.FILES['video']
        # desc = request.POST['desc']
        # user = request.user
        # speaker = Speaker.objects.get(speaker_id=user.id)
        # VideoCourse.objects.remove(title=title, course_id=course, image=rasm, video=video,
        #                            description=desc, author_id=speaker.id)
        return JsonResponse(data={})


# kursni o'chirish
@login_required(login_url='login')
def DeleteCourse(request):
    if chekUser(request):
        return chekUser(request)
    print('555')
    pk = request.POST['course_id']
    if request.method == 'POST':
        user = Speaker.objects.filter(speaker_id=request.user.id)[0]
        Course.objects.filter(author_id=user.id, pk=pk).delete()
    return redirect('speaker-courses')


# speaker rasmnini o'zgartirish
@login_required(login_url='login')
def ChangePhoto(request):
    if chekUser(request):
        return chekUser(request)
    if request.method == 'POST':
        rasm = request.FILES['rasm']
        sp = Speaker.objects.get(speaker_id=request.user.id)
        try:
            if sp.image != '':
                os.remove(BASE_DIR + sp.image.url)
            if sp.image2 is not None:
                os.remove(BASE_DIR + sp.image2.url)
            sp.image = rasm
            sp.image2 = rasm
            sp.save()
        except:
            sp.image = rasm
            sp.image2 = rasm
            sp.save()
        return redirect('profile')
    else:
        return redirect('profile')


def is_auth(user):
    return user.is_authenticated and user.admin_set.count() > 0


# speaker credit kartasini qo'shish
@login_required(login_url='login')
def CreditCard(request):
    card_name = request.GET.get('card_name')
    card_number = request.GET.get('card_number')
    card_date = request.GET.get('card_date')

    sp = Speaker.objects.get(speaker_id=request.user.id)
    if card_number != "" and card_number is not None:
        sp.card_number = card_number

    if card_name != "" and card_name is not None:
        sp.card_name = card_name

    if card_date != "" and card_date is not None:
        sp.card_date = card_date

    sp.save()
    return JsonResponse({})


# speaker profilini tahrirlash
@login_required(login_url='login')
def EditProfile(request):
    if chekUser(request):
        return chekUser(request)
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        tel = request.POST['tel']
        kasbi = request.POST['kasbi']
        country = request.POST['country']
        city = request.POST['city']
        try:
            logo = request.FILES['logo']
        except:
            logo = None
        compony = request.POST['compony']
        both_date = request.POST['both_date']
        malumot = request.POST['description']
        user = request.user
        SpeakerSerializer(request.POST, files=request.FILES)
        sp = Speaker.objects.get(speaker_id=request.user.id)
        if first_name != '':
            user.first_name = first_name
            user.save()
        if last_name != '':
            user.last_name = last_name
            user.save()

        if country != '':
            sp.country = country
        if city != '':
            sp.city = city

        if both_date != '':
            sp.both_date = both_date
        if logo is not None:
            sp.logo = logo

        if tel != '':
            sp.phone = tel

        if compony != '':
            sp.compony = compony

        if kasbi != '':
            sp.kasbi = kasbi

        if malumot != '':
            sp.description = malumot
        sp.save()
        return redirect('profile')
    else:
        return redirect('profile')


# pul yechish so'rovlarini olish
@login_required(login_url='login')
def get_billing(request):
    speaker = Speaker.objects.get(speaker=request.user)
    date = datetime.datetime.today()
    billings = Billing.objects.filter(speaker=speaker)
    if speaker.cash > 50000:
        if billings.count() == 0:
            bil = Billing.objects.create(speaker=speaker)
            status = 1
        else:
            num2 = date.toordinal()
            num1 = billings.last().date_pay.toordinal()
            if num2 > num1 + 30:
                bil = Billing.objects.create(speaker=speaker)
                status = 1
            else:
                status = 22
    else:
        status = 11
    return JsonResponse({"status": status})


# parolni o'zgartirish
@login_required(login_url='login')
def EditPassword(request):
    if chekUser(request):
        return chekUser(request)
    user = request.user
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        conf_password = request.POST['conf_password']
        if new_password == conf_password:
            if check_password(old_password, user.password):
                user.set_password(new_password)
                user.save()
                return redirect('logout')
            else:
                messages.error(request, 'Amaldagi parol xato!')
                return redirect('profile')
        else:
            messages.error(request, 'Parolni tasdiqlash mos kelmadi')
            return redirect('profile')
    else:
        return redirect('profile')


# usernameni o'zgartirish
@login_required(login_url='login')
def EditUsername(request):
    if chekUser(request):
        return chekUser(request)
    if request.method == 'POST':
        username = request.POST['username']
        cn = User.objects.filter(username=username).count()
        if cn > 0:
            messages.error(request, "Bunday username oldin ro'yxatga olingan!")
            return redirect('profile')
        else:
            user = request.user
            user.username = username
            user.save()
            return redirect('profile')
    else:
        return redirect('profile')


@login_required(login_url='login')
def SpeakerAjax(request):
    user = request.user
    speaker = Speaker.objects.get(speaker_id=user.id)
    rasm = speaker.image
    name = user.first_name + " " + user.last_name
    if rasm != '':
        rasm = rasm.url
    else:
        rasm = None
    data = {
        'name': name,
        'rasm': rasm,
        'cash': speaker.cash
    }

    return JsonResponse(data)


def chack_kurs(request):
    id = request.GET.get('id')
    cr = Course.objects.get(id=id)
    if cr.upload_or_youtube == "Youtube":
        status = '1'
    else:
        status = '0'
    data = {
        'status': status
    }
    return JsonResponse(data)


def chekUser(request):
    if request.user.is_authenticated:
        user = request.user
        try:
            sp = Speaker.objects.get(speaker_id=user.id)
            # if sp.status == 1:
            #     return redirect('waiting')
            # elif sp.status == 0:
            #     url = 'reg-full?id=' + str(sp.id)
            #     return HttpResponseRedirect(url)
            if sp.status == 0:
                url = 'reg-full?id=' + str(sp.id)
                return HttpResponseRedirect(url)
            else:
                return False
        except Speaker.DoesNotExist:
            ad = Admin.objects.get(admin_id=user.id)
            if ad is not None:
                return redirect('backoffice-home')
            else:
                return redirect('logout')
        except Admin.DoesNotExist:
            return redirect('logout')
    else:
        return redirect('login')


def DataChart(request):
    dt = datetime.datetime.today()
    year = dt.year
    data = []
    user = request.user
    speaker = Speaker.objects.get(speaker=user)
    for i in range(1, 13):
        sana_start = str(year) + '-' + str(i) + "-01"
        if i == 12:
            sana_end = str(year + 1) + "-01-01"
        else:
            sana_end = str(year) + '-' + str(i + 1) + "-01"
        course = Course.objects.filter(date__gte=sana_start, date__lt=sana_end, author=speaker).count()
        video = VideoCourse.objects.filter(date__gte=sana_start, date__lt=sana_end, course__author=speaker).count()
        sell = Order.objects.filter(date__gte=sana_start, date__lt=sana_end, course__author=speaker).count()

        dts = {
            'period': i, 'smartphone': course, 'windows': video, 'mac': sell
        }
        data.append(dts)

    return JsonResponse({'data': data})


# kurs yaratish
@login_required(login_url='login')
def AddCourse(request):
    if chekUser(request):
        return chekUser(request)
    if request.method == 'POST':
        name = request.POST['name']
        turi = request.POST['turi']
        author = request.user
        speaker = Speaker.objects.get(speaker_id=author.id)
        image = request.FILES['image']
        price = request.POST['price']
        category = request.POST['category']
        video_or_url = request.POST['upload_or_url']
        descrip = request.POST['desc']
        add = Course.objects.create(name=name, turi=turi, author_id=speaker.pk, image=image, category_id=category,
                                    upload_or_youtube=video_or_url, description=descrip, price=price)
        return redirect('speaker-courses')



# kursni o'zgartirish
@login_required(login_url='login')
def ChangeCourse(request):
    if chekUser(request):
        return chekUser(request)
    if request.method == 'POST':
        id = request.POST['course_id']
        name = request.POST['name']
        turi = request.POST['turi']
        discount = request.POST['discount']
        author = request.user
        speaker = Speaker.objects.get(speaker_id=author.id)
        try:
            image = request.FILES['image']
        except:
            image = None
        price = request.POST['price']
        category = request.POST['category']
        video_or_url = request.POST['upload_or_url']
        descrip = request.POST['desc']
        add = Course.objects.filter(id=id).update(name=name, turi=turi, author_id=speaker.pk, category_id=category,
                                                  upload_or_youtube=video_or_url, description=descrip,
                                                  discount=discount, price=price)
        if image is not None:
            try:
                cr = Course.objects.get(id=id)
                cr.image = image
                cr.save()
            except:
                pass
    return redirect('speaker-courses')


from rest_framework.response import Response

from home.sms import sms_send


def check_phone_number(request):
    phone_number = request.POST.get('phone_number')

    if Speaker.objects.filter(phone=phone_number).exists():
        data = {
            "status": False,
            "data": "Speaker already exists"
        }
        return JsonResponse(data, status=405)
    if phone_number is not None:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        print(phone_number)
        res = sms_send(
            phone_number,
            settings.SMS_REGISTER_TEXT + code
        )
        phone_number = str(phone_number)
        phone_number = phone_number.replace("+", "")
        if res is not None:
            PhoneCodeSpeaker.objects.update_or_create(phone=phone_number, defaults={'code': code})
            data = {
                "status": True,
                "data": "SMS send"
            }
        else:
            data = {
                "status": False,
                "data": "SMS doesn't send"
            }
    else:
        data = {
            "status": False,
            "data": "Telefon nomer xato."
        }
    return JsonResponse(data, status=200)


# ro'yhatdan o'tish
def check_code(request):
    phone_number = request.POST.get('phone_number')
    sp_code = request.POST.get('code')
    phone_number = str(phone_number)
    phone_number = phone_number.replace("+", "")
    ph_c = PhoneCodeSpeaker.objects.filter(phone=phone_number, code=sp_code)
    if ph_c.count() > 0:
        data = {
            "success": True,
            "error": "",
            "message": "Code Tasdiqlandi!",
            "data": {
                "phone": phone_number,
                "code": sp_code
            }
        }
    else:
        data = {
            "success": False,
            "error": "",
            "message": "Code Tasdiqlanmadi!",
        }
    return JsonResponse(data, status=200)


from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)


@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def full_register(request):
    try:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        gender = request.POST.get('gender')
        code = request.POST.get('code')
        phone_number = str(phone_number)
        phone_number = phone_number.replace('+', '')
        ph_c = PhoneCodeSpeaker.objects.filter(phone=phone_number, code=code)
        if password1 == password2:
            if ph_c.count() > 0:
                if User.objects.filter(username=phone_number).exists():
                    us = User.objects.get(username=phone_number)
                    us.password = make_password(password1)
                    us.save()
                else:
                    us = User.objects.create(
                        username=phone_number,
                        password=make_password(password1),
                        first_name=first_name,
                        last_name=last_name
                    )
                if Speaker.objects.filter(phone=phone_number).exists():
                    data = {
                        "success": False,
                        "error": "Bu speaker oldin royhatdan otkan.",
                        "message": "",
                    }
                else:
                    sp = Speaker.objects.create(
                        phone=phone_number, speaker=us, status=1, gender=gender
                    )
                    ser = SpeakerSerializer(sp)
                    token = tokens.RefreshToken.for_user(sp)
                    tk = {
                        "refresh": str(token),
                        "access": str(token.access_token)
                    }
                    data = {
                        "success": True,
                        "error": "",
                        "message": "Speaker yaratildi!",
                        "data": {
                            "speaker": ser.data,
                            "token": tk
                        }
                    }
            else:
                data = {
                    "success": False,
                    "error": "Telefon raqam yoki tasdiq kodi xato!",
                    "message": "",
                }
        else:
            data = {
                "success": False,
                "error": "Parollar bir-biriga to'g'ri kelmaydi!",
                "message": "",
            }

    except Exception as er:
        data = {
            "success": False,
            "error": "{}".format(er),
            "message": ""
        }
    return JsonResponse(data)


@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def LogIn(request):
    try:
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        phone = str(phone).replace('+', '')
        try:
            speaker = Speaker.objects.filter(phone=phone).first()
            us = User.objects.get(username=phone)

            if check_password(password, us.password):
                ser = SpeakerLoginSerializer(speaker)
                token = tokens.RefreshToken.for_user(speaker.speaker)
                tk = {
                    "refresh": str(token),
                    "access": str(token.access_token)
                }
                data = {
                    "success": True,
                    "error": "",
                    "message": "Kirish tasdiqlandi!",
                    "data": {
                        "speaker": {
                            'first_name': us.first_name,
                            'last_name': us.last_name,
                            'phone': phone,
                            'email': us.email
                        },
                        "token": tk
                    }
                }
            else:
                data = {
                    "success": False,
                    "error": "Telefon raqam yoki password xato!!",
                    "message": ""
                }
        except Speaker.DoesNotExist:
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
    return JsonResponse(data)


@api_view(['post'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def updateProfile(request):
    try:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        job = request.POST.get("job")
        company = request.POST.get('company')
        gender = request.POST.get('gender')
        try:
            logo = request.FILES.get('logo')
        except:
            logo = None
        try:
            image = request.FILES.get('image')
        except:
            image = None
        both_day = request.POST.get("both_day")
        phone = request.POST.get('phone')
        country = request.POST.get("country")
        region = request.POST.get("region")
        email = request.POST.get('email')
        region_obj = Region.objects.get(id=region)
        country_obj = Country.objects.get(id=country)

        us = request.user
        sp = Speaker.objects.filter(speaker=request.user).first()

        if first_name != '':
            us.first_name = first_name
            us.save()
        if last_name != '':
            us.last_name = last_name
            us.save()
        if email != '':
            us.email = email
            us.save()

        if country != '':
            sp.country = country

        if gender != '':
            sp.gender = gender

        if region != '':
            sp.city = region

        if both_day != '':
            birth_day = both_day.split("-")
            sp.both_date = datetime.date(int(birth_day[0]), int(birth_day[1]), int(birth_day[2]))
        if logo is not None:
            sp.logo = logo

        if image is not None:
            sp.image = image

        if phone != '':
            sp.phone = phone

        if company != '':
            sp.compony = company

        if job != '':
            sp.kasbi = job

        sp.save()

        data = {
            'success': True,
            'message': 'Profil update qilindi'
        }
    except:
        data = {
            'success': False,
            'message': 'Xatolik!!!'
        }
    return JsonResponse(data, status=200)


@api_view(['post'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def updateCardProfile(request):
    try:
        try:
            image = request.FILES.get('image')
        except:
            image = None

        card_number = request.POST.get('card_number')
        card_date = request.POST.get('card_date')
        card_name = request.POST.get('card_name')
        us = request.user
        sp = Speaker.objects.filter(speaker=us).first()

        if image is not None:
            sp.image = image

        if card_number != '':
            sp.card_number = card_number

        if card_date != '':
            sp.card_date = card_date

        if card_name != '':
            sp.card_name = card_name

        sp.save()

        data = {
            'success': True,
            'message': 'Profil card update qilindi'
        }
    except:
        data = {
            'success': False,
            'message': 'Xatolik!!!'
        }

    return JsonResponse(data, status=200)


@api_view(['post'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def updatePasswordProfile(request):
    try:
        try:
            image = request.FILES.get('image')
        except:
            image = None

        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        us = request.user
        sp = Speaker.objects.filter(speaker=us).first()
        if check_password(old_password, us.password):
            if new_password == confirm_password:
                if image is not None:
                    sp.image = image
                    sp.save()

                if new_password != '':
                    us.password = make_password(new_password)

                us.save()

                data = {
                    'success': True,
                    'message': 'Parol almashtirildi'
                }
            else:
                data = {
                    'success': False,
                    'message': 'Parollar birxil emas'
                }
        else:
            data = {
                'success': False,
                'message': 'Eski parol xato'
            }
    except:
        data = {
            'success': False,
            'message': 'Xatolik!!!'
        }

    return JsonResponse(data, status=200)


def reset_password_check(request):
    phone_number = request.POST.get('phone_number')

    if not Speaker.objects.filter(phone=phone_number).exists():
        data = {
            "status": False,
            "data": "Bunday speaker mavjud emas"
        }
        return JsonResponse(data, status=405)
    if phone_number is not None:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        res = sms_send(
            phone_number,
            settings.SMS_REGISTER_TEXT + code
        )
        phone_number = str(phone_number)
        phone_number = phone_number.replace("+", "")
        if res is not None:
            PhoneCodeSpeaker.objects.update_or_create(phone=phone_number, defaults={'code': code})
            data = {
                "status": True,
                "data": "SMS send"
            }
        else:
            data = {
                "status": False,
                "data": "SMS doesn't send"
            }
    else:
        data = {
            "status": False,
            "data": "Telefon nomer xato."
        }
    return JsonResponse(data, status=200)


def ResetPassword(request):
    try:
        phone_number = request.POST.get('phone_number')
        sp_code = request.POST.get('code')
        phone_number = str(phone_number)
        phone_number = phone_number.replace("+", "")
        ph_c = PhoneCodeSpeaker.objects.filter(phone=phone_number, code=sp_code)
        if ph_c.count() > 0:
            speaker = Speaker.objects.filter(phone=phone_number).first()
            ser = SpeakerLoginSerializer(speaker)
            token = tokens.RefreshToken.for_user(speaker.speaker)
            new_token = token.access_token
            new_token.set_exp(lifetime=datetime.timedelta(minutes=180))
            tk = {
                "refresh": str(token),
                "access": str(new_token)
                # "access": str(token.access_token)
            }
            data = {
                "success": True,
                "error": "",
                "message": "Code Tasdiqlandi!",
                "data": {
                    "phone": phone_number,
                    "token": tk
                }
            }
        else:
            data = {
                "success": False,
                "message": "Code Tasdiqlanmadi!"
            }
    except:
        data = {
            "success": False,
            "message": "Xatolik!!!"
        }
    return JsonResponse(data, status=200)


@api_view(['post'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def reset_password_done(request):
    try:
        user = request.user
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            data = {
                "success": True,
                "message": "Parol almashtirildi"
            }
        else:
            data = {
                "success": False,
                "message": "Parollar birxil emas"
            }
    except:
        data = {
            "success": False,
            "message": "Xatolik!"
        }
    return JsonResponse(data, status=200)


@api_view(['get'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def get_speaker(request):
    try:
        user = request.user
        us = DjangoUserSerializers(user)
        sp = Speaker.objects.get(speaker_id=user.id)
        sr = GetSpeakerSerializer(sp)
        try:
            country = Country.objects.get(id=sp.country)
        except:
            country = None
        try:
            region = Region.objects.get(id=sp.city)
        except:
            region = None
        if country is not None and region is not None:
            data = {
                "success": True,
                "speaker_data": {
                    "speaker": us.data,
                    "other": sr.data,
                    "country_name": country.name,
                    "region_name": region.name
                }
            }
        else:
            data = {
                "success": True,
                "speaker_data": {
                    "speaker": us.data,
                    "other": sr.data
                }
            }
    except Exception as e:
        data = {
            "success": False,
            "message": "{}".format(e)
        }
        return JsonResponse(data, status=405)
    return Response(data)


# parolni qayta tiklash
def ResetPasswordChek(request):
    if request.user.is_authenticated:
        return redirect('speaker-home')
    if request.method == "POST":
        code = request.POST.get('phone_code')
        phone = request.POST.get('phone')
        print(code, phone)
        if code and phone and User.objects.filter(username=phone).exists():
            user = User.objects.filter(username=phone).first()
            print(user)
            if code == user.password:
                check = True
            else:
                check = False
        else:
            check = False
        return JsonResponse({"check": check}, safe=False)


# parolni o'zgartirish
def ChangePassowrd(request):
    id = request.GET.get("kod")
    return render(request, 'speaker/resetpasword2.html', {"user_id": id})


def SetPasswordChange(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password2 == password:
            try:
                user = User.objects.get(id=user_id)
                user.set_password(password)
                user.save()
                login(request, user)
                return redirect('speaker-home')
            except User.DoesNotExist:
                messages.error(request, "Bunday foydalanuvchi mavjud emas!")
                url = 'change-password-r?kod=' + str(user_id)
                return HttpResponseRedirect(url)
        else:
            messages.error(request, "UTakroriy parol mos kelmadi!")
            url = 'change-password-r?kod=' + str(user_id)
            return HttpResponseRedirect(url)


def ResetPassworddd(request):
    check = False
    phone = None
    if request.user.is_authenticated:
        return redirect('speaker-home')
    if request.method == "POST":
        code = request.POST.get('code')
        phone = request.POST.get('phone')

        if code and phone and User.objects.filter(username=phone).exists():
            user = User.objects.filter(username=phone).first()
            if code == user.password:
                url = 'change-password-r?kod=' + str(user.id)
                return HttpResponseRedirect(url)
            else:
                check = True
        else:
            return redirect('resset-password')
    return render(request, 'speaker/resetpasword.html', {'check': check, 'phone': phone})


# To'liq ro'yhatdan o'tish
@login_required(login_url='login')
def FullReg(request):
    user = request.user
    try:
        sp = Speaker.objects.get(speaker_id=user.id)
        if sp.status == 1:
            return redirect('waiting')
        elif sp.status == 0:
            pass
        else:
            return redirect('speaker-home')
    except Speaker.DoesNotExist:
        ad = Admin.objects.get(admin_id=user.id)
        if ad is not None:
            return redirect('backoffice-home')
        else:
            return redirect('logout')
    except Admin.DoesNotExist:
        return redirect('logout')
    id = request.GET.get('id')
    if request.method == 'POST':
        try:
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            password = request.POST['password']
            job = request.POST['job']
            description = request.POST['description']
            message = request.POST['message']
            has_course = request.POST.get('has_course')
            id = request.POST['id']
            sp = Speaker.objects.get(id=id)
            us = sp.speaker
            us.first_name = first_name
            us.last_name = last_name
            us.password = make_password(password)
            us.save()
            if has_course is not None:
                sp.has_course = True
            sp.description = description
            sp.kasbi = job
            sp.message = message
            sp.status = 1
            sp.save()
            return redirect('waiting')
        except:
            return render(request, 'speaker/signup2.html', {'id': id})

    return render(request, 'speaker/signup2.html', {'id': id})


@login_required(login_url='login')
def Waiting(request):
    user = request.user
    try:
        sp = Speaker.objects.get(speaker_id=user.id)
        if sp.status == 1:
            pass
        elif sp.status == 0:
            url = 'reg-full?id=' + str(user.id)
            return HttpResponseRedirect(url)
        else:
            return redirect('speaker-home')
    except Speaker.DoesNotExist:
        ad = Admin.objects.get(admin_id=user.id)
        if ad is not None:
            return redirect('backoffice-home')
        else:
            return redirect('logout')
    except Admin.DoesNotExist:
        return redirect('logout')
    return render(request, 'speaker/waiting.html')


def LogOut(request):
    logout(request)
    return redirect('login')
