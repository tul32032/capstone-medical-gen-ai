from django.urls import path
from .views import AdminAnalyticsApi, RecordQueryApi

urlpatterns = [
    path("analytics/admin/", AdminAnalyticsApi.as_view(), name="admin-analytics"),
    path("analytics/record-query/", RecordQueryApi.as_view(), name="record-query"),
]
