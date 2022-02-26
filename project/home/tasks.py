from datetime import date, timezone,  timedelta
from background_task import background
from home.models import Course, Discount
from django.db.models import Q


@background(schedule=70)
def delete_discount():
    discounts = Discount.objects.filter(expire_day=date.today())
    for discount in discounts:
        course = discount.course
        course.discount = 0
        course.save()
        discount.delete()


@background(schedule=60)
def set_discount_to_random_courses():
    courses = Course.objects.filter(Q(discount=0) | Q(discount=None))
    courses = courses.order_by('?')[:10]
    for course in courses:
        amount = course.price * 0.5
        expire_day = date.today() + timedelta(days=7)
        Discount.objects.create(
            course=course, amount=amount, expire_day=date.today())
        course.discount = amount
        course.save()


set_discount_to_random_courses()
delete_discount()
