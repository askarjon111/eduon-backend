from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.schedules import crontab
from datetime import date, timedelta
from home.models import Course, Discount
from django.db.models import Q
from celery.utils.log import get_task_logger
import datetime


logger = get_task_logger(__name__)


@shared_task(name='set_discount_to_random_courses')
def set_discount_to_random_courses(*args, **kwargs):
    courses = Course.objects.filter(
        Q(discount=0) & Q(is_confirmed=True) & Q(price__gt=0))
    courses = courses.order_by('?')[:10]
    for course in courses:
        amount = course.price * 0.5
        expire_day = datetime.datetime.now() + timedelta(days=7)
        Discount.objects.create(
            course=course, amount=amount, expire_day=expire_day)
        course.discount = amount
        course.save()



def delete_discount(*args, **kwargs):
    discounts = Discount.objects.filter(expire_day__lte=datetime.datetime.now())
    if discounts:
        for discount in discounts:
            print('course')
            course = discount.course
            course.discount = 0
            course.save()
            discount.delete()
    else:
        print('discount topilmadi')


@shared_task(name='delete_discount_task')
def delete_discount_task(*args, **kwargs):
    delete_discount()


@shared_task(name='print_test')
def print_test(*args, **kwargs):
    print('asdada')


def run_tasks():
    print_test.apply_async(countdown=5)
    return True
