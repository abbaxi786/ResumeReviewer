from django.urls import path
from .views import FileMessage,GetSingleResume
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from api.users.auth import register,login



urlpatterns = [
    path("api/file/", FileMessage),
    path("api/login/",login),
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/register/", register, name="register"),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    path('api/resume/<int:resume_id>/', GetSingleResume),
]