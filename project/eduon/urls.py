
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import user_passes_test

from decorator_include import decorator_include

from home.click import TestView
from home.views import Page404
from home.viewset import DidUserBuy
from rest_framework.authtoken import views
from simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)

from . import router


handler404 = Page404


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('backoffice/', include('backoffice.urls')),
    path('quizzes/', include('quiz.urls')),
    path('api1234/', include(router.router.urls)),
    path('api/did-user-buy/', DidUserBuy.as_view(), name="is-user-bought"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-token-auth/', views.obtain_auth_token),
    path('api/paycom/', include('paycom.urls')),
    path('api/uniredpay/', include('uniredpay.urls')),
    path('click/transaction/', TestView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)