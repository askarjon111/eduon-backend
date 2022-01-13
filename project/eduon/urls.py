"""eduon URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
# !!!!!! Dear developer, write clean code !!!!!! #
# !!!!!!!!!! Don't make us scold you !!!!!!!!!!! #
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #


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
    # path('backoffice/', decorator_include(user_passes_test(lambda user: user.is_authenticated and user.admin_set.count() > 0), 'backoffice.urls')),

    path('api1234/', include(router.router.urls)),
    path('api/did-user-buy/', DidUserBuy.as_view(), name="is-user-bought"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api-token-auth/', views.obtain_auth_token),
    path('api/paycom/', include('paycom.urls')),
    path('api/uniredpay/', include('uniredpay.urls')),
    path('click/transaction/', TestView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)