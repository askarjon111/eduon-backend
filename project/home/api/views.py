from datetime import datetime

from django.http import JsonResponse
from moviepy.editor import VideoFileClip
from django.db.models import Sum, Avg, Q
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, get_object_or_404, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.backends import TokenBackend

from home.api.pagination import CourseCustomPagination
from home.api.serializers import GetCourseSerializer, LanguageSerializer
from home.models import CategoryVideo, Speaker, Rank, Course, VideoCourse, Order, LikeOrDislike, VideoViews, \
    AboutUsNote, Users, Language


################################################################################################
#                                      SERIALIZERS                                             #
################################################################################################

class VideoCourseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoCourse
        exclude = ['author', 'views_count']


class AboutUsNoteModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUsNote
        exclude = ['created_at']


class UsersModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = (
            'first_name',
            'last_name',
            'country',
            'region',
            'phone',
            'card_number',
            'card_expire',
            'email',
            'image',
            'age',
            'gender',
            'job',
            'get_country_name',
            'get_region_name'
        )


################################################################################################
#                               course.html dagi APIView                                       #
################################################################################################


class CourseSpeakerAPIView(APIView):
    """
    URL: /courses/
    course.html ga chiqadigan hamma ma'lumotlar chiqadi
    """

    permission_classes = []
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        categories = CategoryVideo.objects.all().values('name', 'image')
        user = request.user
        speaker = Speaker.objects.get(speaker_id=user.id)
        # speaker = Speaker.objects.get(id=1016)
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
                logo = request.build_absolute_uri(course.author.logo.url)
            except:
                logo = None

            try:
                img = request.build_absolute_uri(course.image.url)
            except:
                img = None

            dt = {
                'name': course.name,
                'price': round(course.price / 1000, 2),
                'price2': course.price,
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
        data = {
            'success': True,
            'message': "Nimadir",
            'data': context,
            'errors': []
        }
        return Response(data)


class UploadVideoAndDocumentAPIView(CreateAPIView):
    """
    URL: /video-upload-add
    url ga POST dan keladigan ma'lumot boyicha db ga save() qiladi
    jonatiladigan field_name lari modelsniki bilan bir xil qilib frontda ozgartirish kerak
    """
    serializer_class = VideoCourseModelSerializer
    queryset = VideoCourse.objects.all()
    permission_classes = []
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        print(self.request)
        speaker = Speaker.objects.get(speaker_id=self.request.user.id)
        # speaker = Speaker.objects.get(id=1016)  # check qilish uchun
        serializer.save(author=speaker)


class VideosAPIView(APIView):
    """
    URL: /courses/id
    url uchun course {id} detail ma'lumotlarini olish
    """
    permission_classes = []
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk=None):
        try:
            course_obj = Course.objects.values().get(id=pk)
        except Exception:
            return Response(status=404)
        if course_obj['upload_or_youtube'] == "Video":
            status = '1'
        else:
            status = '0'
        course_data = {
            # 'id': course_obj.id,
            # 'name': course_obj.name,
            'course_obj': course_obj,
            "status": status
        }

        try:
            videos = VideoCourse.objects.filter(course_id=pk).values().order_by("place_number")
            videolar = []
            for video in videos:
                likes = LikeOrDislike.objects.filter(value=1, video_id=video['id']).count()
                dislikes = LikeOrDislike.objects.filter(value=-1, video_id=video['id']).count()
                views = VideoViews.objects.filter(video_id=video['id']).count()

                dt = {
                    'likes': likes,
                    'dislikes': dislikes,
                    'views': views,
                    'video': video,
                }

                videolar.append(dt)

            context = {
                'videolar': videolar,
                'vd': 'active',
                'course_obj': course_data,
            }

        except Exception as e:
            print(e)
            context = {
                'videos': [],
                'vd': 'active',
                'course_obj': course_data,
            }
        data = {
            'success': True,
            'errors': [],
            'message': "Nimadirlar",
            'data': context
        }
        return Response(data)

    def delete(self, request, pk=None):
        try:
            Course.objects.filter(id=pk).delete()
        except Exception as e:
            print(e)
        return Response({"success": True, "message": "O'chirildi"}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk=None):
        name = request.data.get('name')
        turi = request.data.get('turi')
        discount = request.data.get('discount')
        author = request.user
        speaker = Speaker.objects.get(speaker_id=author.id)
        # speaker = Speaker.objects.get(id=1016)
        image = request.FILES.get('image', None)
        price = request.data.get('price')
        category = request.data.get('category')
        video_or_url = request.data.get('upload_or_youtube')
        descrip = request.data.get('description')
        try:
            add = Course.objects.filter(id=pk).update(name=name, turi=turi, author_id=speaker.pk, category_id=category,
                                                      upload_or_youtube=video_or_url, description=descrip,
                                                      discount=discount, price=price)
        except Exception as e:
            print(e)
            return Response({"success": False, 'message': "Xatolik"}, status=status.HTTP_400_BAD_REQUEST)
        if image is not None:
            try:
                cr = Course.objects.get(pk=pk)
                cr.image = image
                cr.save()
            except Exception as e:
                print(e)
        data = {
            "success": True,
            'message': "/courses/ ga redirect qilish kerak"
        }
        return Response(data, status=status.HTTP_202_ACCEPTED)


class ChangeCourseAPIView(APIView):
    permission_classes = []
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        pk = request.data('course_id')
        name = request.data('name')
        turi = request.data('turi')
        discount = request.data('discount')
        author = request.user
        speaker = Speaker.objects.get(speaker_id=author.id)
        image = request.FILES.get('image', None)
        price = request.data('price')
        category = request.data('category')
        video_or_url = request.data('upload_or_url')
        descrip = request.data('desc')
        add = Course.objects.filter(id=pk).update(name=name, turi=turi, author_id=speaker.pk, category_id=category,
                                                  upload_or_youtube=video_or_url, description=descrip,
                                                  discount=discount, price=price)
        if image is not None:
            try:
                cr = Course.objects.get(id=pk)
                cr.image = image
                cr.save()
            except Exception as e:
                print(e)
        data = {
            "success": True,
            'message': "/courses/ ga redirect qilish kerak"
        }
        return Response(data, status=202)


class DeleteCourseAPIView(APIView):
    permission_classes = []
    authentication_classes = [JWTAuthentication]
    """
    Permissionlar qoyish kerak !!!
    """

    def post(self, request):
        pk = request.data.get('course_id')
        user = Speaker.objects.filter(speaker_id=request.user.id).first()
        Course.objects.filter(author_id=user.id, pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeleteVideoAPIView(APIView):
    permission_classes = []
    authentication_classes = [JWTAuthentication]
    """
    Permissionlar qoyish kerak !!!
    """

    def delete(self, request):
        try:
            pk = request.data.get('video_id')
            VideoCourse.objects.filter(id=pk).delete()
            data = {
                "success": True,
                "message": "Video o'chirildi"
            }
        except:
            data = {
                "success": False,
                "message": "Xatolik"
            }
            return Response(data, status=405)
        return Response(data, status=200)

    def put(self, request):
        try:
            pk = request.data.get('pk')
            title = request.data.get('title')
            url = request.data.get('url')
            video_url = request.data.get('video')
            description = request.data.get('description')
            link = request.data.get('description')
            place_number = request.data.get('place_number')
            image = request.data.get('image')
            video = VideoCourse.objects.get(id=pk)
            if title is not None:
                video.title = title
            if url is not None:
                video.url = url
            if video_url is not None:
                video.video = video_url
            if description is not None:
                video.description = description
            if link is not None:
                video.link = link
            if place_number is not None:
                video.place_number = place_number
            if image is not None:
                video.image = image
            video.save()
            data = {
                "success": True,
                "message": "Ma'lumotlar o'zgartirildi"
            }
        except:
            data = {
                "success": False,
                "message": "Xatolik"
            }
            return Response(data, status=405)
        return Response(data, status=200)


class AddCourseAPIView(APIView):
    permission_classes = []
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        author = request.user
        name = request.data.get('name')
        description = request.data.get('description')
        language = request.data.get('language')
        category = request.data.get('category')
        child_category = request.data.get('child_category')
        video_or_url = request.data.get('upload_or_youtube')
        image = request.FILES.get('image')
        turi = request.data.get('turi')
        speaker = Speaker.objects.get(speaker_id=author.id).first()
        price = request.data.get('price', 0)
        if speaker is None:
            return Response({'success': True,
                             'message': "Speaker topilmadi"})
        try:
            add = Course.objects.create(author_id=speaker.pk,
                                        name=name, turi=turi,
                                        description=description,
                                        language=language,
                                        category_id=category,
                                        child_category=child_category,
                                        image=image,
                                        upload_or_youtube=video_or_url,
                                        price=price)
        except Exception as e:
            print(e)
            return Response({'message': "Qaysidir fieldlar to'gri kiritilmadi"},
                                status=status.HTTP_400_BAD_REQUEST)
        data = {
            'success': True,
            'message': '/courses/ ga yonaltirish kerak'
        }
        return Response(data)


################################################################################################
#                               home.html dagi APIView                                       #
################################################################################################

class HomeSpeakerAPIView(APIView):
    permission_classes = []
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = self.request.user
        speaker = Speaker.objects.filter(speaker=user).first()
        # speaker = Speaker.objects.filter(pk=126).first()
        if speaker is None:
            return Response({'message': "Speaker mavjud emas"}, status=status.HTTP_400_BAD_REQUEST)
        course_count = Course.objects.filter(author_id=speaker.id).count()
        rank = Rank.objects.filter(speaker_id=speaker.id).values()
        sell_count = Order.objects.filter(course__author_id=speaker.id).count()
        reyting = rank.aggregate(total_summa=Sum('value')).get('total_summa')
        orders = Order.objects \
                     .filter(course__author_id=speaker.id) \
                     .select_related('user', 'course') \
                     .values('id', 'summa', 'bonus', 'sp_summa', 'discount', 'date', 'user__first_name',
                             'user__last_name', 'user__region', 'user__region__name') \
                     .order_by('-id')[0:50]

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
        data = {
            'success': True,
            'message': "Nimadirlar",
            'data': context,
            'errors': []
        }
        return Response(data)


################################################################################################
#                               Rewrite Courses APIView                                        #
################################################################################################


class GetCourseListAPIView(ListAPIView):
    queryset = Course.objects.filter(is_confirmed=True)
    serializer_class = GetCourseSerializer
    # pagination_class = CourseCustomPagination
    filter_backends = [SearchFilter]
    search_fields = ['name']
    authentication_classes = []
    permission_classes = []

    def list(self, request, *args, **kwargs):
        category = request.query_params.get('category', False)
        rank = request.query_params.getlist('rank')
        date = request.query_params.get('date', False)
        toifa = request.query_params.get('toifa', False)
        toifa_sort = request.query_params.get('toifa_sort', False)

        message = ""

        qs = self.queryset.annotate(rank=Avg('rankcourse__course_value'))
        if category == '':
            return Response([], status=status.HTTP_404_NOT_FOUND)
        if rank:
            qs = qs.filter(rank__gte=min(rank))
        if category:
            qs = qs.filter(category=category)
        if date:
            try:
                year, month, day = date.split('-')
                d = datetime(int(year), int(month), int(day), 0, 0)
                qs = qs.filter(date__gte=d)
            except Exception as e:
                print(e)
                message += "date: Wrong format\nMust be 'YYYY-mm-dd'"
        if toifa and toifa in ("Bepul", "Pullik"):
            qs = qs.filter(turi=toifa)
            if toifa == "Pullik" and toifa_sort and toifa_sort in ('asc', 'desc'):
                if toifa_sort == 'asc':
                    qs = qs.order_by('price')
                else:
                    qs = qs.order_by('-price')

        queryset = self.filter_queryset(qs.distinct())

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data = {
            "success": True,
            'message': message,
            # "error": serializer.errors,
            "data": serializer.data
        }
        return Response(data)


class NewCourseListAPIView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = GetCourseSerializer
    authentication_classes = []
    permission_classes = []

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(is_confirmed=True)).order_by('-id')[:10]

        serializer = self.get_serializer(queryset, many=True)
        data = {
            "success": True,
            "data": serializer.data
        }
        return Response(data)


class AboutUsNoteModelViewSet(viewsets.ModelViewSet):
    queryset = AboutUsNote.objects.all()
    serializer_class = AboutUsNoteModelSerializer
    permission_classes = []
    authentication_classes = []


class GetStatisticsAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        try:
            courses = Course.objects.all()
            speakers = Speaker.objects.all()
            users = Users.objects.all()
            category = CategoryVideo.objects.all()
            data = {
                "success": True,
                "error": "",
                "message": "Statistika olindi!",
                "data": {
                    "course_count": courses.count(),
                    "speaker_count": speakers.count(),
                    "users_count": users.count(),
                    "category_count": category.count()
                }
            }
        except Exception as er:
            data = {
                "success": False,
                "error": "{}".format(er),
                "message": ""
            }

        return Response(data)


class TopCourseAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        try:
            query = Course.objects.filter(is_top=1).order_by('-id')
            if len(query) > 10:
                query = query[:10]
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


@api_view(['get', 'put'])
@authentication_classes([])
@permission_classes([])
def users_retrieve_update_api_view(request):
    token = request.META.get('HTTP_AUTHORIZATION', False)
    if token:
        access_token = token.split(' ')[-1]
        get_token = TokenBackend(algorithm='HS256').decode(access_token, verify=False)
        user_id = get_token.get('user_id')
        if user_id is None:
            return Response({'message': "Bunday `User` mavjud emas"}, status=400)
        # Userni check qilib olib keyin GET va POST ga ajratildi
        if request.method in ['PUT']:
            serializer = UsersModelSerializer(instance=Users.objects.get(id=user_id), data=request.data,
                                              context={'request': request})
            if serializer.is_valid():
                serializer.save(user_id=user_id)
                return Response({'success': True, 'message': "O'zgartirildi", 'data': serializer.data})
            else:
                return Response({'success': False, 'message': "given data is not valid", 'error': serializer.errors})
        else:
            data = UsersModelSerializer(Users.objects.get(id=user_id)).data
            return Response(data)
    return Response("Authorization qo'yilmagan", status=status.HTTP_400_BAD_REQUEST)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def get_cash_balance(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION', False)

        access_token = token.split(' ')[-1]
        get_token = TokenBackend(algorithm='HS256').decode(access_token, verify=False)
        user_id = get_token.get('user_id')
        if user_id is None:
            return Response({'message': "Bunday foydalanuchi mavjud emas"}, status=400)
        user = Users.objects.get(id=user_id)
        data = {
            "success": True,
            "cash": user.cash,
            "bonus": user.bonus
        }
    except Users.DoesNotExist:
        data = {
            "success": False,
            "message": "Bunday foydalanuvchi mavjud emas"
        }
        return JsonResponse(data, status=405)
    except:
        data = {
            "success": False,
            "message": "Xatolik!!!"
        }
        return JsonResponse(data, status=405)
    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def filter_by_cost(request):
    try:
        minimum = request.GET.get("from")
        maximum = request.GET.get("to")
        courses = Course.objects.filter(Q(price__gt=minimum), Q(price__lt=maximum))
        sr = GetCourseSerializer(courses, many=True)
        data = {
            "success": True,
            "data": sr.data
        }
    except Exception as e:
        data = {
            "success": False,
            "error": "{}".format(e)
        }
        return JsonResponse(data, status=405)
    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def filter_by_language(request):
    try:
        language = request.GET.get("language")
        courses = Course.objects.filter(language=language)
        sr = GetCourseSerializer(courses, many=True)
        data = {
            "success": True,
            "data": sr.data
        }
    except Exception as e:
        data = {
            "success": False,
            "error": "{}".format(e)
        }
        return JsonResponse(data, status=405)
    return Response(data)


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def get_languages(request):
    try:
        lang = Language.objects.all()
        languages = LanguageSerializer(lang, many=True)
        data = {
            "success": True,
            "data": languages.data
        }
    except Exception as e:
        data = {
            "success": False,
            "error": "{}".format(e)
        }
        return JsonResponse(data, status=405)
    return Response(data)
