from django.urls import path

from .views import *

urlpatterns = [
    path('', payment_view, name='index'),
]
