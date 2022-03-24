from __future__ import absolute_import
import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduon.settings')
import django
django.setup()
app = Celery('eduon')
from django.conf import settings
from home.models import Course, Discount
from datetime import date, timedelta
from celery.schedules import crontab
from django.db.models import Q
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
# set the default Django settings module for the 'celery' program.

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))