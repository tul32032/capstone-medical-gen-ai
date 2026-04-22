from django.urls import path
from .views import AdminAnalyticsApi, DeleteDocumentApi

urlpatterns = [
    path("analytics/admin/", AdminAnalyticsApi.as_view(), name="admin-analytics"),
    path("analytics/document/", DeleteDocumentApi.as_view(), name="delete-document"),
]
