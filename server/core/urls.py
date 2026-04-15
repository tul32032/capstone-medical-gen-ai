from django.urls import path
from .views import ChatProxyView, UploadFile, ChatHistoryView

urlpatterns = [
    path("chat/", ChatProxyView.as_view(), name="chat"),
    path("upload/", UploadFile.as_view(), name="upload"),
    path("history/", ChatHistoryView.as_view(), name="history")
]