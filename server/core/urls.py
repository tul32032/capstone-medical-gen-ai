from django.urls import path
from .views import ChatProxyView

urlpatterns = [
    path("chat/", ChatProxyView.as_view(), name="chat"),
]
