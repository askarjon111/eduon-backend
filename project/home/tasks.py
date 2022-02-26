from datetime import date, timezone
from background_task import background
from home.models import Course, Discount
from django.db.models import Q


@background(schedule=60)
def delete_discount():
    courses = Discount.objects.filter(expire_day=date.today())
    courses.update(course__discount=0)
    courses.delete()
