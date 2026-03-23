from django.urls import path
from .views import ChatProxyView, UploadFile

urlpatterns = [
    path("chat/", ChatProxyView.as_view(), name="chat"),
    path("upload/", UploadFile.as_view(), name="upload"),
]
