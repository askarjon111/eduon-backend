from django.db.models import Sum
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class RankCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RankCourse
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class DjangoUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class SpeakerSerializer(serializers.ModelSerializer):
    speaker = UserSerializers(read_only=True)
    speaker_rank = serializers.SerializerMethodField()

    def get_speaker_rank(self, obj):
        print(f'test')
        cr = RankCourse.objects.filter(course__author=obj.id)
        count = cr.filter(speaker_value__gt=0).count()
        value = cr.aggregate(value=Sum('speaker_value')).get('value')
        if value is None:
            value = 0
        if count > 0:
            return {"rank": round(value / count, 2), "count": count}
        else:
            return {"rank": 0, "count": 0}

    class Meta:
        model = Speaker
        fields = ['id', 'speaker', 'kasbi', 'compony', 'image', 'description', 'is_top', 'logo',
                  'speaker_rank']


class VideoCourseSerializer(serializers.ModelSerializer):
    author = SpeakerSerializer(read_only=True)
    speaker_rank = serializers.SerializerMethodField()
    course_rank = serializers.SerializerMethodField()
    content_rank = serializers.SerializerMethodField()
    video_rank = serializers.SerializerMethodField()

    class Meta:
        model = VideoCourse
        fields = '__all__'

    def get_speaker_rank(self, obj):
        cr = RankCourse.objects.filter(course_id=obj.course.id)
        count = cr.filter(speaker_value__gt=0).count()
        value = cr.aggregate(value=Sum('speaker_value')).get('value')
        if value is None:
            value = 0
        if count > 0:
            return {"rank": round(value / count, 2), "count": count}
        else:
            return {"rank": 0, "count": 0}

    def get_course_rank(self, obj):
        cr = RankCourse.objects.filter(course_id=obj.course.id)
        value = cr.aggregate(value=Sum('course_value')).get('value')
        count = cr.filter(course_value__gt=0).count()
        if value is None:
            value = 0
        if count > 0:
            return {"rank": round(value / count, 2), "count": count}
        else:
            return {"rank": 0, "count": 0}

    def get_content_rank(self, obj):
        cr = RankCourse.objects.filter(course_id=obj.course.id)
        count = cr.filter(content_value__gt=0).count()
        value = cr.aggregate(value=Sum('content_value')).get('value')
        if value is None:
            value = 0
        if count > 0:
            return {"rank": round(value / count, 2), "count": count}
        else:
            return {"rank": 0, "count": 0}

    def get_video_rank(self, obj):
        cr = RankCourse.objects.filter(course_id=obj.course.id)
        count = cr.filter(video_value__gt=0).count()
        value = cr.aggregate(value=Sum('video_value')).get('value')
        if value is None:
            value = 0
        if count > 0:
            return {"rank": round(value / count, 2), "count": count}
        else:
            return {"rank": 0, "count": 0}


class VideoCourseGetSerializer(serializers.ModelSerializer):
    author = SpeakerSerializer(read_only=True)
    turi = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    speaker_rank = serializers.SerializerMethodField()
    course_rank = serializers.SerializerMethodField()
    content_rank = serializers.SerializerMethodField()
    video_rank = serializers.SerializerMethodField()

    class Meta:
        model = VideoCourse
        fields = '__all__'

    def get_turi(self, obj):
        return obj.course.turi

    def get_speaker_rank(self, obj):
        cr = RankCourse.objects.filter(course_id=obj.course.id)

        value = cr.aggregate(value=Sum('speaker_value')).get('value')
        if value is None:
            value = 0
        if cr.count() > 0:
            return round(value / cr.count(), 2)
        else:
            return 0

    def get_course_rank(self, obj):
        cr = RankCourse.objects.filter(course_id=obj.course.id)
        value = cr.aggregate(value=Sum('course_value')).get('value')
        if value is None:
            value = 0
        if cr.count() > 0:
            return round(value / cr.count(), 2)
        else:
            return 0

    def get_content_rank(self, obj):
        cr = RankCourse.objects.filter(course_id=obj.course.id)
        value = cr.aggregate(value=Sum('content_value')).get('value')
        if value is None:
            value = 0
        if cr.count() > 0:
            return round(value / cr.count(), 2)
        else:
            return 0

    def get_video_rank(self, obj):
        cr = RankCourse.objects.filter(course_id=obj.course.id)
        value = cr.aggregate(value=Sum('video_value')).get('value')
        if value is None:
            value = 0
        if cr.count() > 0:
            return round(value / cr.count(), 2)
        else:
            return 0

    def get_price(self, obj):
        return obj.course.price


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            "first_name",
            "last_name",
            "country",
            "region",
            "phone",
            "email",
            "image",
            "regdate",
            "last_sean",
            "cash",
            "gender",
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class UsersSerializerEdit(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'age', 'job', 'country', 'region', 'status',
                  'bonus']


class UserEditModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name', 'email', 'age', 'job', 'country', 'region']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryVideo
        fields = '__all__'


class LikeOrDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeOrDislike
        fields = '__all__'


class RankSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields = '__all__'


class VideoViewsSerialzier(serializers.ModelSerializer):
    author = SpeakerSerializer(read_only=True)

    class Meta:
        model = VideoViews
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    author = SpeakerSerializer(read_only=True)
    sell_count = serializers.SerializerMethodField()
    view = serializers.SerializerMethodField()
    course_rank = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

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

    def get_view(self, obj):
        videos = VideoCourse.objects.filter(course_id=obj.id)
        views = videos.aggregate(total=Sum('views_count')).get('total')
        if views == None:
            views = 0
        return views


class DjangoCourseSerializer(serializers.ModelSerializer):
    author = SpeakerSerializer(read_only=True)
    sell_count = serializers.SerializerMethodField()
    view = serializers.SerializerMethodField()
    course_rank = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

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

    def get_view(self, obj):
        videos = VideoCourse.objects.filter(course_id=obj.id)
        views = videos.aggregate(total=Sum('views_count')).get('total')
        if views is None:
            views = 0
        return views

    def get_comment_count(self, obj):
        comments = Comment.objects.filter(course_id=obj.id)
        return comments.count()


class TopCourseSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = TopCourse
        fields = '__all__'


class EduonTafsiyasiSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = EduonTafsiyasi
        fields = '__all__'


class FavoriteCourseSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = FavoriteCourse
        fields = '__all__'


class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = '__all__'


class OrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class CommentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name', 'image']


class CommentVideoSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer(read_only=True)

    class Meta:
        model = CommentCourse
        fields = "__all__"


class SpeakerCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class SpeakerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ['id']


class SpeakerRegisterModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ['id', 'phone']


class SpeakerLoginSerializer(serializers.ModelSerializer):
    speaker = DjangoUserSerializers()
    speaker_rank = serializers.SerializerMethodField()

    def get_speaker_rank(self, obj):
        cr = RankCourse.objects.filter(course__author=obj.id)
        count = cr.filter(speaker_value__gt=0).count()
        value = cr.aggregate(value=Sum('speaker_value')).get('value')
        if value is None:
            value = 0
        if count > 0:
            return {"rank": round(value / count, 2), "count": count}
        else:
            return {"rank": 0, "count": 0}

    class Meta:
        model = Speaker
        fields = ['id', 'speaker', 'kasbi', 'compony', 'image', 'description', 'is_top', 'logo',
                  'speaker_rank']


class GetSpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = '__all__'
