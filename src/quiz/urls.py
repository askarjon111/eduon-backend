from django.urls.conf import path, include

from .views import get_quiz_view, submit_quiz_view

urlpatterns = [
    path('quiz/<int:pk>', get_quiz_view, name='quiz'),
    path('submit', submit_quiz_view, name='submit'),
]
