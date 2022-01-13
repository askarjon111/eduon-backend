from django.db.models import Sum, Q
from django.http import JsonResponse
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .permissions import *
import eduon
from .serializers import *
from django.contrib.auth.hashers import check_password
from .models import *
import os


def get_user_course(request):
    param = request.query_params
    user = param.get("user", False)
    course = param.get("order", False)
    return user, course


class DidUserBuy(APIView):

    def get(self, request):
        user, course = get_user_course(request)
        try:
            order = Order.objects.get(user=user, course=course)
            serializer = OrderSerializers(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            data = {
                "did_user_buy": False
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)


class CountryViewset(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'edit']


class RegionViewset(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']


class VideoCourseViewset(viewsets.ModelViewSet):
    queryset = VideoCourse.objects.all()
    serializer_class = VideoCourseSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    @action(methods=['get'], detail=False)
    def single(self, request):
        id = request.GET.get('id')
        likes = LikeOrDislike.objects.filter(value=1, video_id=id).count()
        dislikes = LikeOrDislike.objects.filter(value=-1, video_id=id).count()
        views = VideoViews.objects.filter(video_id=id).count()
        video = VideoCourse.objects.get(id=id)
        vs = VideoCourseSerializer(video)
        dt = {
            'likes': likes,
            'dislikes': dislikes,
            'views': views,
            'video': vs.data
        }
        return Response(data=dt)


class SpeakerViewset(viewsets.ModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    @action(methods=['get'], detail=False)
    def top(self, request):
        speakers = Speaker.objects.extra(
            select={
                'rating': 'SELECT SUM(value) FROM home_rank WHERE home_rank.speaker_id=home_speaker.id',
                'count': 'SELECT COUNT(id) FROM home_rank WHERE home_rank.speaker_id=home_speaker.id',
                'course': 'SELECT COUNT(id) FROM home_course WHERE home_course.author_id=home_speaker.id',
                'sells': 'SELECT COUNT(id) FROM home_order WHERE home_order.course_id in (SELECT id FROM home_course '
                         'WHERE home_course.author_id=home_speaker.id)'
            },
        ).filter(status=2, is_top=1)
        data = []
        for sp in speakers:
            if sp.count == 0:
                reyting = 0
            elif sp.rating is None:
                reyting = 0
            else:
                reyting = sp.rating / sp.count
            try:
                image = sp.image.url
            except:
                image = None
            try:
                image2 = sp.image2.url
            except:
                image2 = None

            try:
                logo = sp.logo.url
            except:
                logo = None

            dt = {
                'id': sp.id,
                'first_name': sp.speaker.first_name,
                'last_name': sp.speaker.last_name,
                'kasbi': sp.kasbi,
                'image': image,
                'image2': image2,
                'reyting': reyting,
                'course': sp.course,
                'logo': logo,
                'description': sp.description,
            }
            data.append(dt)
        return Response(data)

    @action(methods=['get'], detail=False)
    def all(self, request):
        speakers = Speaker.objects.extra(
            select={
                'rating': 'SELECT SUM(value) FROM home_rank WHERE home_rank.speaker_id=home_speaker.id',
                'count': 'SELECT COUNT(id) FROM home_rank WHERE home_rank.speaker_id=home_speaker.id',
                'course': 'SELECT COUNT(id) FROM home_course WHERE home_course.author_id=home_speaker.id',
                'sells': 'SELECT COUNT(id) FROM home_order WHERE home_order.course_id in (SELECT id FROM home_course '
                         'WHERE home_course.author_id=home_speaker.id)'
            },
        ).filter(status=2)
        data = []
        for sp in speakers:
            if sp.count == 0:
                reyting = 0
            elif sp.rating is None:
                reyting = 0
            else:
                reyting = sp.rating / sp.count
            try:
                image = sp.image.url
            except:
                image = None
            try:
                image2 = sp.image2.url
            except:
                image2 = None

            dt = {
                'id': sp.id,
                'first_name': sp.speaker.first_name,
                'last_name': sp.speaker.last_name,
                'kasbi': sp.kasbi,
                'image': image,
                'image2': image2,
                'reyting': reyting,
                'course': sp.course,
                'description': sp.description,
            }
            data.append(dt)
        return Response(data)

    @action(methods=['get'], detail=False)
    def single(self, request):
        id = request.GET.get('id')
        speaker = Speaker.objects.get(id=id)
        rank = Rank.objects.filter(speaker_id=speaker.id)
        reyting = rank.aggregate(total_summa=Sum('value')).get('total_summa')
        course = Course.objects.filter(author_id=speaker.id).count()

        if reyting is None:
            reyting = 0
        count = rank.count()
        if count == 0:
            ry = reyting
        else:
            ry = reyting / count
        if speaker.image:
            img = speaker.image.url
        else:
            img = None

        data = {
            'id': speaker.id,
            'first_name': speaker.speaker.first_name,
            'last_name': speaker.speaker.last_name,
            'description': speaker.description,
            'image': img,
            'reyting': ry,
            'course': course
        }

        return Response(data)

    @action(methods=['get'], detail=False)
    def course(self, request):
        id = request.GET.get('id')
        cr = Course.objects.filter(author_id=id)
        sr = CourseSerializer(cr, read_only=True, many=True)
        return Response(sr.data)


class CommentViewset(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']


class CommentCourseViewset(viewsets.ModelViewSet):
    queryset = CommentCourse.objects.all().order_by('-id')
    serializer_class = CommentVideoSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    @action(methods=['post'], detail=False)
    def add_comment(self, request):
        user = request.POST.get('user')
        course = request.POST.get('course')
        comment = request.POST.get('comment')
        CommentCourse.objects.create(comment=comment, user_id=user, course_id=course)
        comments = CommentCourse.objects.filter(course_id=course).order_by('-id')
        ser = CommentVideoSerializer(comments, many=True)
        return Response(ser.data)

    @action(methods=['get'], detail=False)
    def get_comments(self, request):
        course = request.GET.get('course')
        comments = CommentCourse.objects.filter(course_id=course).order_by('-id')
        ser = CommentVideoSerializer(comments, many=True)
        return Response(ser.data)


class UsersViewset(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    def list(self, request, *args, **kwargs):
        return JsonResponse(data=[], safe=False)

    @action(methods=['POST'], detail=False)
    def fullreg(self, request):
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        job = request.data['job']
        age = request.data['age']
        id = request.data['id']
        country = request.data['country']
        region = request.data['region']
        bon = RegBonus.objects.last()
        fy = Users.objects.get(id=id)
        fy.first_name = first_name
        if bon.summa is not None:
            fy.bonus += bon.summa
            summa = bon.summa
        else:
            summa = 0
        fy.last_name = last_name
        fy.job = job
        fy.age = age
        if country != 'null':
            fy.country = Country.objects.get(id=country)
        if region != 'null':
            fy.region = Region.objects.get(id=region)
        fy.save()
        return Response(data={"summa": summa})

    @action(methods=['POST'], detail=False)
    def reg(self, request):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        phone = request.data.get('phone')
        password = request.data.get('password')
        ref = request.data.get('ref')
        sp = Speaker.objects.filter(own_ref_code=ref)
        usr_ref = Users.objects.filter(own_ref_code=ref)
        if sp.count() > 0 or usr_ref.count() > 0:
            ref = ref
        else:
            ref = None
        usr = Users.objects.create(
            first_name=first_name, last_name=last_name,
            phone=phone, password=password, parent_ref_code=ref
        )
        ser = self.get_serializer_class()(usr)
        return Response(ser.data)

    @action(methods=['GET'], detail=False)
    def checkuser(self, request):
        phone = request.GET.get('phone')

        if Users.objects.filter(phone=phone).exists():
            return Response({'message': 'This number is already registered!', 'status': 'error'})
        return Response({'message': 'this number is available', 'status': 'success'})

    @action(methods=['POST'], detail=False)
    def editPassword(self, request):
        password = request.data['password']
        user = request.data['user']
        usr = Users.objects.get(id=user)
        usr.password = make_password(password)
        usr.save()
        return Response({})

    @action(methods=['POST'], detail=False)
    def editPasswordweb(self, request):
        password = request.data['password']
        phone = request.data['phone']
        usr = Users.objects.filter(phone=phone).first()
        usr.password = make_password(password)
        usr.save()
        return Response({})

    @action(methods=['POST'], detail=False)
    def editphoto(self, request):
        user_id = request.data['user']
        image = request.data['image']
        user = Users.objects.get(id=user_id)
        try:
            os.remove(user.image.path)
        except:
            pass
        user.image = image
        user.save()
        data = {
            'image': user.image.url
        }
        return Response(data)

    @action(methods=['GET'], detail=False)
    def login(self, request):
        phone = request.GET.get('phone')
        password = request.GET.get('password')
        try:
            spk = Users.objects.get(phone=phone)
            if not check_password(password, spk.password):
                data = {
                    'status': 403,
                    'message': 'Telefon raqam yoki password xato!',
                }
            else:
                users = UsersSerializer(spk)
                data = {
                    'status': 200,
                    'user': users.data,
                }
        except Users.DoesNotExist:
            data = {
                'status': 404,
                'message': 'Bunday foydalanuvchi mavjud emas!',
            }
        return Response(data)


class CategoryViewset(viewsets.ModelViewSet):
    queryset = CategoryVideo.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    @action(methods=['get'], detail=False)
    def course(self, request):
        id = request.GET.get('id')
        cr = Course.objects.filter(category_id=id)
        sr = CourseSerializer(cr, read_only=True, many=True)
        return Response(sr.data)


class LikeOrDislikeViewset(viewsets.ModelViewSet):
    queryset = LikeOrDislike.objects.all()
    serializer_class = LikeOrDislikeSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    @action(methods=['post'], detail=False)
    def addlike(self, request):
        user = request.data['user']
        video = request.data['video']
        value = request.data['value']
        type = request.data['type']
        vd = VideoCourse.objects.get(id=video)
        course = vd.course
        try:
            lk = LikeOrDislike.objects.get(user_id=user, video_id=video)
            if type == 'off' and value == 1:
                lk.delete()
                course.like = course.like - 1
                course.save()
            elif type == 'off' and value == -1:
                lk.delete()
                course.like = course.dislike - 1
                course.save()
            elif int(value) == 1 and lk.value != 1:
                course.like = course.like + 1
                if course.dislike > 0:
                    course.dislike = course.dislike - 1
                    course.save()
            elif int(value) == -1 and lk.value != -1:
                course.dislike = course.dislike + 1
                if course.like > 0:
                    course.like = course.like - 1
                    course.save()
            lk.value = value
            lk.save()
        except LikeOrDislike.DoesNotExist:
            LikeOrDislike.objects.create(user_id=user, video_id=video, value=value)
            if int(value) == 1:
                course.like = course.like + 1
                course.save()
            elif int(value) == -1:
                course.dislike = course.dislike + 1
                course.save()

        data = {
            'status': value
        }
        return Response(data)

    @action(methods=['post'], detail=False)
    def checklike(self, request):
        user = request.data['user']
        video = request.data['video']
        try:
            lk = LikeOrDislike.objects.get(user_id=user, video_id=video)
            value = lk.value
        except LikeOrDislike.DoesNotExist:
            value = 0

        data = {
            'status': value
        }
        return Response(data)


class RankViewset(viewsets.ModelViewSet):
    queryset = Rank.objects.all()
    serializer_class = RankSerialzier
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    @action(methods=['post'], detail=False)
    def checkrank(self, request):
        user = request.data['user']
        speaker = request.data['speaker']
        try:
            lk = Rank.objects.filter(user_id=user, speaker_id=speaker)
            if lk.count() > 0:
                lks = Rank.objects.filter(speaker_id=speaker)
                val = lks.aggregate(total_summa=Sum('value')).get('total_summa')
                if val is None:
                    value = 0
                else:
                    value = val / lks.count()
            else:
                value = 0

        except LikeOrDislike.DoesNotExist:
            value = 0

        data = {
            'status': value
        }
        return Response(data)


class VideoViewsViewset(viewsets.ModelViewSet):
    queryset = VideoViews.objects.all()
    serializer_class = VideoViewsSerialzier
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    @action(methods=['get'], detail=False)
    def history(self, request):
        user = request.GET.get('user')
        videos = VideoViews.objects.filter(user_id=user).order_by('-id')[0:10]
        data = []
        for video in videos:
            ser = VideoCourseGetSerializer(video.video)
            data.append(ser.data)
        return Response(data)

    @action(methods=['post'], detail=False)
    def viewer(self, request):
        user = request.data['user']
        video = request.data['video']
        vd = VideoCourse.objects.get(id=video)
        course = vd.course
        viewer = VideoViews.objects.filter(user_id=user, video_id=video).count()
        if viewer == 0:
            course.view = course.view + 1
            course.save()
            VideoViews.objects.create(user_id=user, video_id=video)
        data = {}
        return Response(data)


class CourseViewset(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    def get_queryset(self):
        original_qs = super(CourseViewset, self).get_queryset()

        ids = []

        for instance in original_qs:
            [ids.append(instance.id) if (
                        instance.videocourse_set.count() > 1 and instance.is_confirmed == True) else None]

        return original_qs.filter(id__in=ids)

    @action(methods=['get'], detail=False)
    def ziyodbekga(self, request):
        rows = self.get_queryset().filter(is_top=1)
        data = []
        for row in rows:
            rn = Rank.objects.filter(speaker_id=row.author_id)
            count = rn.count()
            values = rn.aggregate(total=Sum('value')).get('total')
            if count == 0 or values is None:
                rnk = 0
            else:
                rnk = values / count
            videos = VideoCourse.objects.filter(course_id=row.id).order_by("place_number")
            views = videos.aggregate(total=Sum('views_count')).get('total')
            if views is None:
                views = 0
            try:
                logo = row.author.logo.url
            except:
                logo = None
            dt = {
                'id': row.id,
                'image': row.image.url,
                'name': row.name,
                'speaker': {
                    'first_name': row.author.speaker.first_name,
                    'last_name': row.author.speaker.last_name,
                    'mark': round(rnk, 2),
                },
                'logo': logo,
                'videos': videos.count(),
                'narxi': row.price,
                'views': views,
                'desc': row.description
            }
            data.append(dt)
        return Response(data)

    @action(methods=['get'], detail=False)
    def top(self, request):
        query = self.get_queryset().filter(is_top=1)
        ser = self.get_serializer_class()(query, many=True)
        return Response(ser.data)

    @action(methods=['get'], detail=False)
    def search(self, request):
        q = request.GET.get('q')
        course = self.get_queryset().filter(Q(name__icontains=q) | Q(author__speaker__first_name__icontains=q) | Q(
            author__speaker__last_name__icontains=q))
        ser = self.get_serializer_class()(course, many=True)
        return Response(ser.data)

    @action(methods=['get'], detail=False)
    def single(self, request):
        id = request.GET.get('id')
        try:
            user = request.GET['user']
            tt = Order.objects.filter(user_id=user, course_id=id)
            if tt.count() > 0:
                status = '1'
            else:
                status = '0'
        except:
            status = 0
        course = self.get_queryset().get(id=id)
        videos = VideoCourse.objects.filter(course_id=course.id).order_by("place_number")
        speaker = Speaker.objects.get(id=course.author_id)
        sp = SpeakerSerializer(speaker, read_only=True)
        vd = VideoCourseSerializer(videos, read_only=True, many=True)
        cr = CourseSerializer(course, read_only=True)
        data = {
            'course': cr.data,
            'speaker': sp.data,
            'videos': vd.data,
            'status': status
        }
        return Response(data)


class TopCourseViewset(viewsets.ModelViewSet):
    queryset = TopCourse.objects.all()
    serializer_class = TopCourseSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    @action(methods=['get'], detail=False)
    def loadmore(self, request):
        num = request.GET.get('num')
        rows = self.get_queryset().order_by('-id')
        if int(num) + 10 <= rows.count():
            data = rows[int(num):int(num) + 10]
        else:
            data = rows[int(num):]
        ser = self.get_serializer_class()(data, many=True)
        return Response(ser.data)


class RankCourseViewset(viewsets.ModelViewSet):
    queryset = RankCourse.objects.all()
    serializer_class = RankCourseSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    @action(methods=['get'], detail=False)
    def user_rank(self, request):
        user = request.GET.get('user')
        course = request.GET.get('course')
        rnk = RankCourse.objects.filter(user_id=user, course_id=course)
        if rnk.count() > 0:
            return Response(RankCourseSerializer(rnk.last()).data)
        else:
            return Response({})

    @action(methods=['POST'], detail=False)
    def setrating(self, request):
        course = request.POST['course']
        user = request.POST['user']
        value = request.POST.get('value')
        turi = request.POST.get('turi')
        rnk = RankCourse.objects.filter(user_id=user, course_id=course)

        if rnk.count() > 0:
            rn = rnk.last()
            if turi == "1":
                rn.course_value = value
            elif turi == "2":
                rn.speaker_value = value
            else:
                rn.tashkil_value = value
            rn.save()
        else:
            if turi == "1":
                rn = RankCourse.objects.create(
                    user_id=user, course_id=course, course_value=value
                )
            elif turi == "2":
                rn = RankCourse.objects.create(
                    user_id=user, course_id=course, speaker_value=value
                )
            else:
                rn = RankCourse.objects.create(
                    user_id=user, course_id=course, tashkil_value=value
                )
        cr = RankCourse.objects.filter(course_id=course)
        value_sp = cr.aggregate(value=Sum('speaker_value')).get('value')
        if value_sp is None:
            value_sp = 0
        value_cr = cr.aggregate(value=Sum('course_value')).get('value')
        if value_cr is None:
            value_cr = 0

        value_tt = cr.aggregate(value=Sum('tashkil_value')).get('value')
        if value_tt is None:
            value_tt = 0
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
        count_tt = cr.filter(tashkil_value__gt=0).count()
        if count_tt > 0:
            rank_tt = round(value_tt / count_tt, 2)
        else:
            rank_tt = 0

        data = {
            "course": {
                "rank": rank_cr,
                "count": count_cr
            },
            "speaker": {
                "rank": rank_sp,
                "count": count_sp
            },
            "tashkil": {
                "rank": rank_tt,
                "count": count_tt
            },
        }
        ser = RankCourseSerializer(rn)
        return Response({'data': ser.data, "rating": data})


class EduonTafsiyasiViewset(viewsets.ModelViewSet):
    queryset = EduonTafsiyasi.objects.all()
    serializer_class = EduonTafsiyasiSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)
    http_method_names = ['get', 'post', 'put']


class UsersEditViewset(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserEditModelSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']


class FavoriteCourseViewset(viewsets.ModelViewSet):
    queryset = FavoriteCourse.objects.all()
    serializer_class = FavoriteCourseSerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    @action(methods=['post'], detail=False)
    def add(self, request):
        course = request.POST['course']
        user = request.POST['user']
        FavoriteCourse.objects.create(user_id=user, course_id=course)
        return Response({})

    def delete(self, request):
        course = request.POST['course']
        user = request.POST['user']
        ad = FavoriteCourse.objects.get(user_id=user, course_id=course)
        ad.delete()
        return Response({})

    @action(methods=['post'], detail=False)
    def get(self, request):
        user = request.POST['user']
        course = FavoriteCourse.objects.filter(user_id=user)
        ser = self.get_serializer_class()(course, many=True)
        return Response(ser.data)


class PaymentHistoryViewset(viewsets.ModelViewSet):
    queryset = PaymentHistory.objects.all()
    serializer_class = PaymentHistorySerializer
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    # @action(methods=['get'], detail=False)
    # def change_cash(self,request):
    #     users = Users.objects.all()
    #     users.update(cash=0,bonus=50000,status=1)
    #     return Response({})
    # @action(methods=['get'], detail=False)
    # def speaker_cash(self,request):
    #     speaker = Speaker.objects.all()
    #     speaker.update(cash=0)
    #     return Response({})

    @action(methods=['POST'], detail=False)
    def createInvois(self, request):
        user = request.data['user']
        summa = int(request.data['summa'])
        add = PaymentHistory.objects.create(user_id=user, summa=summa)
        data = {
            'marchent_trans_id': add.id
        }
        return Response(data)

    @action(methods=['POST'], detail=False)
    def pay(self, request):
        id = request.data['id']
        invois = request.data['invois']
        payment_id = request.data['payment_id']
        status = request.data['status']
        py = PaymentHistory.objects.get(id=id)
        py.invois = invois
        py.payment_id = payment_id
        py.status = status
        py.save()
        user = py.user
        user.cash = user.cash + py.summa
        user.save()
        return Response({})

    @action(methods=['POST'], detail=False)
    def pay_web(self, request):
        payment_id = request.data['payment_id']
        status = request.data['status']
        summa = request.data['summa']
        user = request.data['user']
        pays = PaymentHistory.objects.filter(payment_id=payment_id, user_id=user, status=status)
        if pays.count() == 0:
            pay = PaymentHistory.objects.create(
                user_id=user, summa=summa,
                payment_id=payment_id, status=status
            )
            usr = pay.user
            usr.cash = usr.cash + int(pay.summa)
            usr.save()

        else:
            usr = Users.objects.get(id=user)
        return Response(UsersSerializer(usr).data)


class OrderViewset(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializers
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    http_method_names = ['get', 'post', 'put']

    def get_discount_obj(self, course):
        try:
            return DiscountCourse.objects.get(course=course)
        except DiscountCourse.DoesNotExist:
            return False

    @action(methods=['post'], detail=False)
    def Add(self, request):
        course = request.data['course']
        user = request.data['user']
        cr = Course.objects.get(id=course)
        usr = Users.objects.get(id=user)
        eduonpay = ContractWithSpeaker.objects.last()
        if eduonpay is None:
            eduonpay = ContractWithSpeaker.objects.create(eduon=30)
        narxi = cr.price - cr.discount
        cash = usr.cash
        bonus = usr.bonus
        row = Order.objects.filter(course_id=course, user_id=user)
        if row.count() > 0:
            message = "Bu kursni oldin sotib olgansiz!"
        else:
            if cash + bonus < narxi:
                message = "Kursni sotib olish uchun hisobingizni to'ldiring!"
            else:
                summa = narxi - bonus
                if summa > 0:
                    usr.cash = usr.cash + bonus - narxi
                    ord = Order.objects.create(course_id=course, user_id=user, summa=summa, bonus=bonus,
                                               discount=cr.discount)
                    usr.bonus = 0
                else:
                    usr.bonus = abs(summa)
                    ord = Order.objects.create(course_id=course, user_id=user, summa=0, bonus=narxi,
                                               discount=cr.discount)

                eduon_summa = eduonpay.eduon
                if usr.parent_ref_code is not None:
                    ref_value = ReferalValue.objects.last()
                    if ref_value is None:
                        ref_value = ReferalValue.objects.create(speaker_value=80, user_value=10)
                    if cr.author.own_ref_code == usr.parent_ref_code:
                        eduon_summa = 100 - ref_value.speaker_value
                        usr.parent_ref_code = None
                    else:
                        us = Users.objects.filter(own_ref_code=usr.parent_ref_code)
                        if us.count() > 0:
                            usr.bonus += int(ref_value.user_value * narxi / 100)
                            usr.parent_ref_code = None
                            uss = us.last()
                            uss.bonus += int(ref_value.user_value * narxi / 100)
                            uss.save()

                speaker = ord.course.author
                speaker.cash = int(round(speaker.cash + ord.summa * (100 - eduon_summa) / 100))
                speaker.save()
                ord.sp_summa = int(round(ord.summa * (100 - eduon_summa) / 100))
                ord.save()
                usr.save()
                message = "Kurs sotib olindi!"
        data = {
            'message': message,
        }
        return Response(data)

    @action(methods=['get'], detail=False)
    def course(self, request):
        user = request.GET['user']
        orders = Order.objects.filter(user_id=user)
        data = []
        for cr in orders:
            ser = CourseSerializer(cr.course)
            data.append(ser.data)
        return Response(data)
