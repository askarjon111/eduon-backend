from django.db.models import Sum
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class CourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ('id', 'title', 'course', 'place_number')


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'title', 'file', 'created_at')


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
    id = serializers.IntegerField(required=False)
    speaker = UserSerializers(read_only=True)
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
        fields = ['id', 'first_name', 'last_name',
                  'email', 'age', 'job', 'country', 'region']


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = CategoryVideo
        fields = ['id', 'name', 'image', 'parent']


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


class CourseTrailerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    video = serializers.CharField(required=False)

    class Meta:
        model = CourseTrailer
        fields = ['id', 'title', 'is_file', 'video', 'url']


class LanguageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Language
        fields = ['id', 'name']


class CourseTagsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = CourseTag
        fields = ['id', 'title']


class WhatYouLearnSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = WhatYouLearn
        fields = ['id', 'title', 'course']


class RequirementsCourseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = RequirementsCourse
        fields = ['id', 'title', 'course']


class ForWhomCourseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ForWhomCourse
        fields = ['id', 'title', 'course']


class CourseSerializer(serializers.ModelSerializer):
    author = SpeakerSerializer(many=False, required=True)
    sell_count = serializers.SerializerMethodField()
    view = serializers.SerializerMethodField()
    image = serializers.CharField(required=False)
    course_rank = serializers.SerializerMethodField()
    trailer = CourseTrailerSerializer(many=False, required=False)
    categories = CategorySerializer(many=True, required=False)
    language = LanguageSerializer(many=False, required=False)
    course_tags = CourseTagsSerializer(many=True, required=False)
    whatyoulearn = WhatYouLearnSerializer(many=True, required=False)
    courserequirements = RequirementsCourseSerializer(
        many=True, required=False)
    forwhom = ForWhomCourseSerializer(many=True, required=False)

    class Meta:
        model = Course
        fields = ['id', 'author', 'name', 'description', 'language', 'level', 'categories', 'upload_or_youtube', 'image', 'trailer', 'course_tags', 'price', 'has_certificate',
                  'logo', 'turi', 'date', 'like', 'dislike', 'discount', 'view', 'course_rank', 'sell_count', 'is_top', 'is_tavsiya', 'is_confirmed', 'whatyoulearn', 'courserequirements', 'forwhom']

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

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        language_data = validated_data.pop('language', None)
        categories_data = validated_data.pop('categories', None)
        trailer_data = validated_data.pop('trailer', None)
        tags_data = validated_data.pop('course_tags', None)
        whatyoulearns_data = validated_data.pop('whatyoulearn', None)
        requirementscourse_data = validated_data.pop(
            'courserequirements', None)
        forwhoms_data = validated_data.pop(
            'forwhom', None)
        author = Speaker.objects.get(id=validated_data.pop('author').get('id'))
        course, _ = Course.objects.get_or_create(
            author=author, **validated_data)

        if language_data:
            new_language, _ = Language.objects.get_or_create(
                name=language_data.get('name'))
            course.language = new_language

        if image:
            course.image = image

        if categories_data:
            for category in categories_data:
                new_category, _ = CategoryVideo.objects.get_or_create(name=category.get(
                    'name'), defaults={'image': category.get('image'), 'parent': category.get('parent')})
                course.categories.add(new_category.id)

        if trailer_data:
            new_trailer, _ = CourseTrailer.objects.get_or_create(defaults={'title': trailer_data.get('title')}, **trailer_data)
            course.trailer = new_trailer

        if tags_data:
            for tag in tags_data:
                new_tag, _ = CourseTag.objects.get_or_create(
                    title=tag.get('title'))
                course.course_tags.add(new_tag.id)

        if whatyoulearns_data:
            for whatyoulearn in whatyoulearns_data:
                new_whatyoulearn, _ = WhatYouLearn.objects.get_or_create(
                    defaults={'title': whatyoulearn.get('title'), 'course': course}, **whatyoulearn)
                course.whatyoulearn.add(new_whatyoulearn)

        if requirementscourse_data:
            for requirement in requirementscourse_data:
                new_requirement, _ = RequirementsCourse.objects.get_or_create(
                    defaults={'title': requirement.get('title'), 'course': course}, **requirement)
                course.courserequirements.add(new_requirement)

        if forwhoms_data:
            for forwhom in forwhoms_data:
                new_forwhom, _ = ForWhomCourse.objects.get_or_create(
                    defaults={'title': forwhom.get('title'), 'course': course}, **forwhom)
                course.forwhom.add(new_forwhom)

        course.save()
        return course

    def update(self, instance, validated_data):
        image = validated_data.pop('image', None)
        language_data = validated_data.pop('language', None)
        categories_data = validated_data.pop('categories', None)
        trailer_data = validated_data.pop('trailer', None)
        tags_data = validated_data.pop('course_tags', None)
        whatyoulearns_data = validated_data.pop('whatyoulearn', None)
        requirementscourse_data = validated_data.pop(
            'courserequirements', None)
        forwhoms_data = validated_data.pop(
            'forwhom', None)
        author = Speaker.objects.get(id=validated_data.pop('author').get('id'))
        # course, _ = Course.objects.filter(id=instance.id)
        
        language_id = language_data.get('id', None)
        if language_id:
            Language.objects.get(id=language_id).update(**language_data)
        else:
            new_language = Language.objects.create(**language_data)
            instance.language = new_language

        if image:
            instance.image = image

        for category in categories_data:
            category_id = category.get('id', None)
            if category_id:
                CategoryVideo.objects.get(id=category_id).update(**category)
            else:
                
                new_category = CategoryVideo.objects.create(**category)
                instance.categories.add(new_category.id)

        trailer_id = trailer_data.get('id', None)
        if trailer_id:
            CourseTrailer.objects.get(id=trailer_id).update(**trailer_data)
        else:
            new_trailer = CourseTrailer.objects.create(title=trailer_data.get(
                'title'), is_file=trailer_data.get('is_file'), video=trailer_data.get('video'))
            instance.trailer = new_trailer
        
        for tag in tags_data:
            tag_id = tag.get('id', None)
            if tag_id:
                CourseTag.objects.get(id=tag_id).update(**tag)
            else:
                CourseTag.objects.create(title=tag.get('title'))
                instance.course_tags.add(tag_id)

        for whatyoulearn in whatyoulearns_data:
            whatyoulearn_id = whatyoulearn.get('id', None)
            if whatyoulearn_id:
                WhatYouLearn.objects.get(id=whatyoulearn_id).update(**whatyoulearn)
            else:
                new_whatyoulearn = WhatYouLearn.objects.create(**whatyoulearn)
                new_whatyoulearn.course = instance
                new_whatyoulearn.save()

        for requirementscourse in requirementscourse_data:
            requirementscourse_id = requirementscourse.get('id', None)
            if requirementscourse_id:
                RequirementsCourse.objects.get(
                    id=requirementscourse_id).update(**requirementscourse)
            else:
                new_requirementscourse = RequirementsCourse.objects.create(
                    **requirementscourse)
                new_requirementscourse.course = instance
                new_requirementscourse.save()

        for forwhom in forwhoms_data:
            forwhom_id = forwhom.get('id', None)
            if forwhom_id:
                ForWhomCourse.objects.get(id=forwhom_id).update(**forwhom)
            else:
                new_forwhom = ForWhomCourse.objects.create(**forwhom)
                new_forwhom.course = instance
                new_forwhom.save()

        return super().update(instance, validated_data)


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
