from django.urls import path
from django.views.decorators.csrf import csrf_exempt
import requests
# from .bot import EduonBot
from eduon import settings
from .views.views import *
from backoffice.views import statistics_views

urlpatterns = [
    path('', HomeView.as_view(), name='backoffice-home'),
    path('sozlamalar', SettingsView.as_view(), name='sozlamalar'),
    path('setContract', setContrantWithSpeaker, name='setContract'),
    path('set-discount', set_discount, name='set-discount'),
    path('speaker', SpeakersView.as_view(), name='backoffice-speaker'),
    path('speaker/course', SpeakerCourse, name='backoffice-speaker-course'),
    path('speaker/<int:pk>', SpeakerDetail.as_view(), name='backoffice-speaker-detail'),
    path('course', CoursesView, name='backoffice-course'),
    path('tolov', Tolov.as_view(), name='backoffice-tolov'),
    path('get-billings-count', get_billings_count, name='get_billings_count'),
    path('accept-billing', accespt_billing, name='accept-billing'),
    path('cancel-billing', cancel_billing, name='cancel-billing'),
    path('users', Foydalanuvchilar, name='backoffice-users'),
    path('charts', AjaxCharts, name='charts'),
    path('tasdiqlash', TasdiqView.as_view(), name='tasdiq'),
    path('tasdiqlash-check', TasdiqOk, name='tasdiq-check'),
    path('count-offer', CountOfferAjax, name='count-offer'),
    path('change-course-status', ChangeCourseStatus, name='change-course-status'),
    path('change-course-status-tavsiya', ChangeCourseStatusTavsiya, name='change-course-status-tavsiya'),
    path('change-speaker-status', ChangeSpeakerStatus, name='change-speaker-status'),
    path('change-user-cash', ChangeCashUser, name='change-user-cash'),
    path('change-user-bonus', ChangeBonusUser, name='change-user-bonus'),
    path('check-phone-number', check_phone_number, name='check-phone-number'),
    path('check-phone-number-reset', check_phone_number_reset, name='check-phone-number-reset'),
    path('set-ref-sp', setReferalValueSp, name='set-ref-sp'),
    path('set-ref-us', setReferalValueUS, name='set-ref-us'),
    path('moliya', moliya, name='moliya'),
    path('set-bonus', setBonusSumma, name='set-bonus'),

    # path('telegram-bot', csrf_exempt(EduonBot.as_view())),
    
    # backoffice statistics
    path('total-count', statistics_views.total_count, name="total_count"),
    path('content-and-auditory', statistics_views.content_and_auditory,
         name="content_and_auditory"),
    path('user-statistics', statistics_views.user_statistics,
         name="user_statistics"),
    path('order-statistics', statistics_views.order_statistics,
         name="order_statistics"),
    path('country-statistics', statistics_views.country_statistics,
         name="country_statistics"),
    path('free-and-paid-courses', statistics_views.free_and_paid_courses,
         name="free_and_paid_courses"),
    path('courses-by-categories', statistics_views.courses_by_categories,
         name="courses_by_categories"),
]

# r = requests.post(settings.SMS_BASE_URL + '/api/auth/login/',
#                   {'email': settings.SMS_EMAIL, 'password': settings.SMS_SECRET_KEY}).json()
# settings.SMS_TOKEN = r['data']['token']

# try:
#     rs = requests.post(settings.SMS_BASE_URL_GLOBAL + '/oauth/token',
#                       {'client_id': settings.SMS_CLIENT_ID, 'secret': settings.SMS_SECRET_KEY_GLOBAL, "expires_in": 3600}).json()
#     settings.SMS_TOKEN_GLOBAL = rs['jwt']
# except:
#     pass
