from backoffice.views.views import check_phone_number
from django.urls.conf import path, include

from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [

    path('', views.HomeSpeaker.as_view(), name='speaker-home'),
    path("api-web/", include("home.api.urls")),
    path('credit-card/', views.CreditCard, name='credit-card'),
    path('courses', views.CourseSpeaker.as_view(), name='speaker-courses'),
    path('add-course', views.AddCourse, name='add-course'),
    path('change-course/', views.ChangeCourse, name='change-course'),
    path('chack-kourse/', views.chack_kurs, name='chack-kourse'),
    path('send_code', csrf_exempt(views.check_phone_number), name='send_code'),
    path('signup', csrf_exempt(views.check_code), name='singup'),
    path('login', views.LogIn, name='login'),
    path('balans', views.BillingView.as_view(), name='balans'),
    path('get_billing', views.get_billing, name='get_billing'),
    path('logout', views.LogOut, name='logout'),
    path('videolar', views.VideosView.as_view(), name='videolar'),
    path('profile', views.ProfileView.as_view(), name='profile'),
    path('speaker-json', views.SpeakerAjax, name='speaker-json'),
    path('changephoto', views.ChangePhoto, name='change-photo'),
    path('edit-profile', views.EditProfile, name='edit-profile'),
    path('edit-username', views.EditUsername, name='edit-username'),
    path('edit-password', views.EditPassword, name='edit-password'),
    path('get_video', views.get_video, name='get_video'),
    path('video-upload', views.VideoUpload.as_view(), name='video-upload'),
    path('video-upload-add', views.UploadVideoPost, name='video-upload-add'),
    path('dockument-upload-add', views.upload_document, name='dockument-upload-add'),
    path('dockument-upload-edit', views.edit_document, name='dockument-upload-edit'),
    path('video-upload-edit', views.EditVideoPost, name='video-upload-edit'),
    path('delete-course', views.DeleteCourse, name='delete-course'),
    path('video-delete', views.deleteVideo, name='video-delete'),
    path('single-video/<int:pk>', views.VideoDetail.as_view(), name='single-video'),
    path('info', views.InfoView.as_view(), name='info'),
    path('reset-password', csrf_exempt(views.ResetPassword), name='resset-password'),
    path('reset-password-check', csrf_exempt(views.reset_password_check), name='resset-password-chek'),
    path('change-password', csrf_exempt(views.reset_password_done), name='change-password'),
    path('reg-full', views.full_register, name='regfull'),
    path('tekshirish', views.Waiting, name='waiting'),
    path('datachart', views.DataChart, name='datachart'),
    path("export-speaker", views.export_speaker, name='export-speaker'),
    path("export-user", views.export_user, name='export-user'),
    path('update-speaker', views.updateProfile, name='speaker_update'),
    path('update-speaker-card', views.updateCardProfile, name='speaker-card-update'),
    path('update-speaker-password', views.updatePasswordProfile, name='speaker-password-update'),
    path('speaker', views.get_speaker, name='get-speaker')
]
