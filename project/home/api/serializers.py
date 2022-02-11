from django.db.models import Sum
from moviepy.editor import VideoFileClip
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from home.models import *
from home.serializers import CourseModuleSerializer, CourseTrailerSerializer, ForWhomCourseSerializer, RequirementsCourseSerializer, WhatYouLearnSerializer
from quiz.models import Quiz
from quiz.serializers import QuizSerializer


class SpeakerGetSerializer(ModelSerializer):
    full_name = SerializerMethodField()
    speaker_rank = SerializerMethodField()
    course_users_count = SerializerMethodField()

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

    def get_full_name(self, obj):
        try:
            usr = User.objects.get(id=obj.speaker.id)
            if usr.first_name is not None and usr.last_name is not None:
                full_name = str(usr.first_name) + " " + str(usr.last_name)
            elif usr.first_name is None:
                full_name = str(usr.last_name)
            elif usr.last_name is None:
                full_name = str(usr.first_name)
            else:
                full_name = ""
        except:
            full_name = ""
        return full_name

    def get_course_users_count(self, obj):
        try:
            usr = Order.objects.filter(course__author_id=obj.id).count()
            courses = Course.objects.filter(author_id=obj.id).count()
            data = {
                'course_count': courses,
                'users_count': usr
            }
        except:
            data = {
                'course_count': 0,
                'users_count': 0
            }
        return data

    class Meta:
        model = Speaker
        fields = [
            'id',
            "full_name",
            "kasbi",
            "compony",
            "description",
            "is_top",
            "logo",
            "image",
            "speaker_rank",
            "course_users_count"
        ]


class LanguageSerializer(ModelSerializer):
    class Meta:
        model = Language
        fields = [
            'id',
            'name'
        ]


class UsersSerializer(ModelSerializer):
    class Meta:
        model = Users
        fields = [
            "id",
            "first_name",
            "last_name",
            "image",
            "cash",
            "bonus",
            "own_ref_code", ]


class UsersCommentSerializer(ModelSerializer):
    class Meta:
        model = Users
        fields = [
            "id",
            "first_name",
            "last_name",
            "image"]


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class RegionSerialzier(ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"


class GetCourseSerializer(ModelSerializer):
    author = SpeakerGetSerializer(read_only=True)
    sell_count = SerializerMethodField()
    course_rank = SerializerMethodField()

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
        fields = "__all__"


class CategorySerializer(ModelSerializer):
    course_count = SerializerMethodField()

    def get_course_count(self, obj):
        course_count = Course.objects.filter(categories=obj.id).count()
        return course_count

    class Meta:
        model = CategoryVideo
        fields = [
            "id",
            "name",
            "image",
            "parent",
            "course_count",
        ]


class VideoSerializer(ModelSerializer):
    class Meta:
        model = VideoCourse
        fields = [
            "id",
            "title",
            "url",
            "video",
            "image",
            "description",
            "is_file",
            "date",
            "views_count",
        ]


class FileOnlyNameSerializer(ModelSerializer):
    class Meta:
        model = File
        fields = [
            "id",
            "name",
            "place_number",
            "courseModule",
        ]

class VideoOnlyNameSerializer(ModelSerializer):
    class Meta:
        model = VideoCourse
        fields = [
            "id",
            "title",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        duration = 0
        if instance.is_file and instance.video and instance.video.url.endswith('.mp4'):
            vv = VideoFileClip(f"{instance.video.path}")
            duration = vv.duration
        rep['duration'] = duration
        return rep


class BoughtedVideoSerializer(ModelSerializer):
    courseModule = CourseModuleSerializer()
    class Meta:
        model = VideoCourse
        fields = [
            "id",
            "title",
            "url",
            "video",
            "image",
            "description",
            "is_file",
            "date",
            "views_count",
            "courseModule",
        ]

class FileSerializer(ModelSerializer):
    class Meta:
        model = File
        fields = [
            "id",
            "speaker",
            "name",
            "file",
            "courseModule",
            "place_number",
        ]


class CourseDetailSerializer(ModelSerializer):
    # trailer = SerializerMethodField()
    modules = SerializerMethodField()
    videos = SerializerMethodField()
    author = SpeakerGetSerializer(read_only=True)
    sell_count = SerializerMethodField()
    course_rank = SerializerMethodField()
    files = SerializerMethodField()
    quizzes = SerializerMethodField()
    categories = CategorySerializer()
    language = LanguageSerializer()
    trailer = CourseTrailerSerializer()
    whatyoulearns = SerializerMethodField()
    requirementscourse = SerializerMethodField()
    forwhoms = SerializerMethodField()
    
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
            return VideoOnlyNameSerializer(videos, many=True).data
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
            return FileOnlyNameSerializer(files, many=True).data
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
        ]


class CourseDetailSpeakerSerializer(ModelSerializer):
    from home.serializers import CategorySerializer
    modules = SerializerMethodField()
    videos = SerializerMethodField()
    author = SpeakerGetSerializer(read_only=True)
    sell_count = SerializerMethodField()
    course_rank = SerializerMethodField()
    files = SerializerMethodField()
    quizzes = SerializerMethodField()
    categories = CategorySerializer()
    language = LanguageSerializer()
    trailer = CourseTrailerSerializer()
    whatyoulearns = SerializerMethodField()
    requirementscourse = SerializerMethodField()
    forwhoms = SerializerMethodField()

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
            modules = CourseModule.objects.filter(course=obj).order_by("place_number")
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
        ]


class BoughtedCourseSerializer(ModelSerializer):
    videos = SerializerMethodField()
    modules = SerializerMethodField()
    files = SerializerMethodField()

    def get_videos(self, obj):
        try:
            videos = VideoCourse.objects.filter(course=obj).order_by("place_number")
            return BoughtedVideoSerializer(videos, many=True).data
        except:
            return []

    def get_modules(self, obj):
        try:
            modules = CourseModule.objects.filter(
                course=obj).order_by("place_number")
            return CourseModuleSerializer(modules, many=True).data
        except:
            return None

    def get_files(self, obj):
        try:
            files = File.objects.filter(
                courseModule__course=obj).order_by("place_number")
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
            "price",
            "categories",
            "date",
            "upload_or_youtube",
            "description",
            "like",
            "dislike",
            "discount",
            "view",
            "is_top",
            "is_tavsiya",
            "videos",
            "modules",
            "files",
        ]


class RatingSerializer(ModelSerializer):
    class Meta:
        model = RankCourse
        fields = "__all__"


class CommentSerializer(ModelSerializer):
    user = UsersCommentSerializer(read_only=True)

    class Meta:
        model = CommentCourse
        fields = ['id', 'user', 'date', 'comment']


class OrderPaymentSerializer(ModelSerializer):
    class Meta:
        model = OrderPayment
        fields = "__all__"

class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        

class BillingSerializer(ModelSerializer):
    class Meta:
        model = Billing
        fields = "__all__"
