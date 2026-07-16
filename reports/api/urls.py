from django.urls import path
from .views import FileMessage

urlpatterns = [
    path("api/file/", FileMessage),
]