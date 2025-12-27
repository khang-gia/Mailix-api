"""MAILIX URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from core.views import login, register, pre_login, generate_otp, verify_otp, generate_otp_with_email, reset_password, change_password
# from core.views import login, register, logout, generate_otp, verify_otp, GoogleLogin, reset_password
from django.conf.urls.static import static
from django.conf import settings

admin.site.site_header = 'Mailix'
admin.site.site_title = 'Mailix'
app_name_prefix = settings.APP_NAME_PREFIX

urlpatterns = [
    path(app_name_prefix + 'admin/', admin.site.urls),
    path(app_name_prefix + 'api-auth/', include('rest_framework.urls')),
    path(app_name_prefix + 'api/v1/', include([
        # path('accounts/', include('allauth.urls')),
        path('auth/', include([
            # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
            # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
            # path('logout/', logout, name='logout'),
            path('login/', login, name='login'),
            path('pre_login/', pre_login, name='pre_login'),
            path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
            # path('verify/', TokenVerifyView.as_view(), name='token_verify'),
            path('register/', register, name='register'),
            # path('registration/', include('dj_rest_auth.registration.urls')),
            # path('google/', GoogleLogin.as_view(), name='google_login'),
            path('otp/', include([
                path('generate/', generate_otp, name='generate_otp'),
                path('generate_email/', generate_otp_with_email, name='generate_otp_with_email'),
                path('verify/', verify_otp, name='verify_otp'),
            ])),
            path('reset_password/', reset_password, name='reset_password'),
            path('change_password/', change_password, name='change_password'),
            # path('', include('dj_rest_auth.urls')),
        ])),
        
        path('core/', include("core.urls")),
        path('consult/', include("consult.urls")),
        path('system/', include("system.urls")),
        path('social/', include("social.urls")),
        # path('fa/', include('fa.urls')),
        # path('analyzer/', include("analyzer.urls")),
        # path('download/', include("download.urls")),
        path('upload/', include("upload.urls")),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    