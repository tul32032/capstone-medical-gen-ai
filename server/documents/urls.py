from django.urls import path

from .views import UploadPdfApi


urlpatterns = [
    path("upload/", UploadPdfApi.as_view(), name="upload-pdf"),
]
