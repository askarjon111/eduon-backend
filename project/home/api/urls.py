from django.urls.conf import path
from rest_framework import routers

from .api_view import (
    full_registration, send_code, verify_code, set_photo, registeration, reset_password,
    get_countries, get_regions, login, get_course, get_boughted_course, buy_course, get_category, course_detail,
    boughted_course_detail, get_top_course, get_speaker, get_rayting, set_rayting, set_comment, get_comment,
    create_invoise, create_invoise_payme, payment_history, get_statistics, get_speaker_data, upload_file,
    get_speaker_courses, verified_courses, verified_speaker_courses, get_courses, get_sell_course_statistics,
    get_user_country_statistics, get_rank_statistics
)
from .views import get_cash_balance, DeleteVideoAPIView, filter_by_cost, filter_by_language, get_languages

urlpatterns = [
    path('send-code/', send_code),
    path('get-countries/', get_countries),
    path('get-regions/', get_regions),
    path('verify-code/', verify_code),
    path('registration/', registeration),
    path('set-photo/', set_photo),
    path('reset-password/', reset_password),
    path('full-registration/', full_registration),
    path('login/', login),
    path('get-course-search/', get_course),
    # path('get-top-course/', get_top_course),
    path('get-boughted-course/', get_boughted_course),
    path('buy-course/', buy_course),
    path('get-speaker/', get_speaker),
    path('get-category/', get_category),
    path('course-detail/', course_detail),
    path('boughted-course-detail/', boughted_course_detail),
    path('get-rayting/', get_rayting),
    path('set-rayting/', set_rayting),
    path('set-comment/', set_comment),
    path('get-comment/', get_comment),
    path('create-invoise-click/', create_invoise),
    path('create-invoise-payme/', create_invoise_payme),
    path('payment-history/', payment_history),
    path('get-statistics/', get_statistics),
    path('get-sell-course-statistics/', get_sell_course_statistics),
    path('get-rank-statistics/', get_rank_statistics),
    path('get-user-country-statics/', get_user_country_statistics),
    path('get-speaker-data/', get_speaker_data),
    path('upload-file/', upload_file),
    path('get-speaker-courses/', get_speaker_courses),
    path('verified-courses/', verified_courses),
    path('verified-speaker-courses/', verified_speaker_courses),
    path('get-courses/', get_courses),
    path('get-cash-balance/', get_cash_balance),
    path('filter-by-cost/', filter_by_cost),
    path('filter-by-language/', filter_by_language),
    path('get-languages/', get_languages)
]

from .views import CourseSpeakerAPIView, UploadVideoAndDocumentAPIView, VideosAPIView, ChangeCourseAPIView, \
    DeleteCourseAPIView, \
    AddCourseAPIView, HomeSpeakerAPIView, GetCourseListAPIView, AboutUsNoteModelViewSet, NewCourseListAPIView, \
    GetStatisticsAPIView, TopCourseAPIView, users_retrieve_update_api_view

urlpatterns += [
    # course.html
    path('courses/', CourseSpeakerAPIView.as_view()),
    path('courses/<int:pk>/', VideosAPIView.as_view()),
    path('video-doc-upload/', UploadVideoAndDocumentAPIView.as_view()),
    path('change-course/', ChangeCourseAPIView.as_view()),
    path('delete-course/', DeleteCourseAPIView.as_view()),
    path('video/', DeleteVideoAPIView.as_view()),
    path('add-course/', AddCourseAPIView.as_view()),
    # home.html
    path('', HomeSpeakerAPIView.as_view()),
    # courses rewrite APIViews
    path('get-course/', GetCourseListAPIView.as_view()),
    path('new-course/', NewCourseListAPIView.as_view()),
    # path('get-statistic/', GetStatisticsAPIView.as_view()),
    path('top-course/', TopCourseAPIView.as_view()),
    # Users retrieve-update
    path('users/', users_retrieve_update_api_view),
]

router = routers.DefaultRouter()
router.register(r'about-us-note', AboutUsNoteModelViewSet, basename='about_us_note')

urlpatterns += router.urls
