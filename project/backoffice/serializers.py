from rest_framework import serializers
from home.models import Course, Order, RankCourse, Speaker
from django.db.models import Count, Q, Sum


class SpeakersListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        first_name = obj.speaker.first_name
        last_name = obj.speaker.last_name
        return f"{first_name} {last_name}"
    
    def get_courses(self, obj):
        courses = Course.objects.filter(author=obj.id)
        return courses.count()
    
    def get_students(self, obj):
        students = Order.objects.filter(course__author_id=obj.id)
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

    class Meta:
        model = Speaker
        fields = ['id', 'name', 'phone', 'courses',
                  'students', 'rating', 'revenue', 'image']
